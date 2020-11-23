
import requests
from secretInfo import headers,base,stid
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
import os
import pandas as pd
import time
# from secretInfo import drive


ihaveapickle = True

def getOrders(status_id=10, i=1):
    url = base + f'v2/orders?status_id={status_id}'\
        + f'&limit=50&page={i}'
    res = requests.get(url, headers = headers)
    return res

def allOrders(status_id=10):
    n = 1
    orders = []
    while getOrders(status_id, i=n).text:
        nthOrders = json.loads(getOrders(status_id, i=n).content)
        orders.extend(nthOrders)
        n += 1
    return orders


def newOrders(test=False):
    # returns json orders object or [] if no new orders

    odf = pd.json_normalize(allOrders())
    odf.external_source = odf.external_source.fillna('').replace('','bigcommerce')
    if ihaveapickle:    
        pickled_odf = pd.read_pickle('orders.pkl')
        new_odf = odf[~odf.id.isin(pickled_odf.id)]
    else:
        odf.to_pickle('orders.pkl')
        new_odf = odf
    
    if len(new_odf) > 0:

        if not test:
            odf.to_pickle('orders.pkl')

        cols = [
            'id',
            'total_inc_tax',
            'items_total',
            'payment_method',
            'payment_provider_id',
            'external_source',
            'external_id',
            'products.url',
        ]
        df = new_odf[cols].astype(
            {
                'id':int,
                'total_inc_tax':float,
                'items_total':int,
                'payment_provider_id':str,
            }
        )
        orders = df.to_dict('records')

        product_keys = [
            'order_id',
            'name',
            'sku',
            'quantity',
            'price_inc_tax',
            'total_inc_tax',
        ]

        full_orders = []
        for order in orders:
            # append products to order via url
            products = requests.get(
                    order.pop('products.url'),
                    headers = headers,
                ).json()
            products = [
                {
                    k:v for k,v in product.items() if k in product_keys
                }
                for product in products
            ]
            for product in products:
                for field in ['price_inc_tax','total_inc_tax']:
                    product[field] = float(product[field]) 
            order.update({'products':products})
            full_orders.append(order)
        return full_orders
    else:
        return []


ecmdf = pd.read_pickle('fromECM.pkl')



def sid():
    sid = str(int(hash(str(time.time()))%1e13))
    time.sleep(1)
    return sid

source_map = {
    'ebay':'EBAY',
    'bigcommerce':'BIGCOMME'
}

prefix_map = {
    'ebay':'EBAY',
    'bigcommerce':'BC',
    '_':'SLS',
    '__':'', # Amazon
    '___':'WSH',
    '____':'RK',
    '_____':'WAL',
    '______':'FB',
    '_______':'QUIV',
    '________':'STRON',
}

payment_map = {
    'Authorize.net':'AUTHORIZE.NET',
    'PayPal':'PAYPAL',
    'Authorize.Net (Google Pay)':'GOOGLE PAY',
    'Amazon Pay':'AMAZON PAY',
    'ebay':'PAYPAL',
    '_':'APPLE PAY',
    '__':'CHASE PAY',
}


def invoice_attrib(order):
    now = time.strftime('%Y-%m-%dT%H:%M:%S')
    invoice_attrib = {
        'invc_sid':sid(),
        'created_date':now,
        'modified_date':now+'-08:00',
        'clerk_name':source_map[order['external_source']],
        'controller':'1',
        'orig_controller':'1',
        'invc_type':'0',
        'status':'2',
        'store_no':'1',
        'sbs_no':'1',
    }
    return invoice_attrib

def tender_attrib(order):
    tender_attrib = {
        'tender_type':'0', # 4 for charges to sideline/amazon etc.
        'tender_no':'1',
        'taken':str(order['total_inc_tax']),
        'amt':str(order['total_inc_tax']),
        'orig_currency_name':payment_map[order['payment_method']],
        'currency_name':payment_map[order['payment_method']],
    }
    return tender_attrib

def comments(order):
    comments = ['','']
    source = order['external_source']
    if source!='bigcommerce':
        comments[0] = (prefix_map[source] + ' ' + order['external_id']).strip()
        comments[1] = 'external'
    else:
        comments[0] = f'BC {order["id"]}'
        comments[1] = str(order['payment_provider_id'])
    return comments

def items(order):
    items = []
    for i,product in enumerate(order['products']):
        sku = product['sku'].split('-')[1].lstrip('0')
        record = ecmdf.fillna('').astype(str)[ecmdf.sku==sku].iloc[0].to_dict()
        item = {
            'item_pos':str(i+1),
            'item_sid':str(record['isid']),
            'qty':str(product['quantity']),
            'orig_price':str(record['pSale']),
            'price':str(product['price_inc_tax']),
        }
        items.append(item)
    return items

def base_items(order):
    base_items = []
    for product in order['products']:
        sku = product['sku'].split('-')[1].lstrip('0')
        record = ecmdf.fillna('').astype(str)[ecmdf.sku==sku].iloc[0].to_dict()
        base_item = {
            'item_sid':str(record['isid']),
            'upc':str(record['UPC']),
            'alu':str(record['sku']),
            'style_sid':str(record['ssid']),
            'dcs_code':record['DCS'],
            'vend_code':record['VC'],
            'description1':record['name'],
            'description2':record['year'],
            'description3':record['alt_color'],
            'description4':record['mpn'],
            'attr':record['color'],
            'siz':record['size'],
        }
        base_items.append(base_item)
    return base_items

class Invoice:
    def __init__(self, order, no):
        c = comments(order)
        self.invoice_attrib = invoice_attrib(order)
        self.invoice_attrib.update({'invc_no':f'{no}'})
        self.comments = comments(order)
        self.tender_attrib = tender_attrib(order)
        self.comments = [
                {
                    'comment_no':'1',
                    'comments':f'{c[0]}'
                },
                {
                    'comment_no':'2',
                    'comments':f'{c[1]}'
                }
            ]
        self.invc_items = [
            {
                'invc_item':i, 
                'invc_base_item':b
            } for i,b in zip(*(items(order), base_items(order)))]

    def to_xml(self):
        invoice = ET.Element('INVOICE',self.invoice_attrib)
        ET.SubElement(invoice,'CUSTOMER')
        ET.SubElement(invoice,'SHIPTO_CUSTOMER')
        ET.SubElement(invoice,'INVC_SUPPLS')
        invc_comments = ET.SubElement(invoice,'INVC_COMMENTS')
        ET.SubElement(invc_comments,'INVC_COMMENT',self.comments[0])
        ET.SubElement(invc_comments,'INVC_COMMENT',self.comments[1])
        ET.SubElement(invoice,'INVC_EXTRAS')
        ET.SubElement(invoice,'INVC_FEES')
        invc_tenders = ET.SubElement(invoice, 'INVC_TENDERS')
        ET.SubElement(invc_tenders,'INVC_TENDER',self.tender_attrib)
        invoice_items = ET.SubElement(invoice,'INVC_ITEMS')
        for item in self.invc_items:
            invc_item = ET.SubElement(invoice_items, 'INVC_ITEM', item['invc_item'])
            ET.SubElement(invc_item, 'INVC_BASE_ITEM', item['invc_base_item'])
        rough_xml = ET.tostring(invoice, 'unicode')
        dom = md.parseString(rough_xml)
        return dom.toprettyxml()

def document(orders, ecm=True, drive='E', stid=f'{stid}'):
    if orders == []:
        print('no new orders found on bigcommerce, make sure completed orders are marked `Completed` in orders page of admin panel')
    else:
        n = len(pd.read_pickle('orders.pkl'))
        header = f'<?xml version="1.0" encoding="UTF-8"?>\n<!-- Created on {time.strftime("%Y-%m-%dT%H:%M:%S")}-08:00 -->\n<!-- V9 STATION -->\n<DOCUMENT>\n<INVOICES>'
        footer = '</INVOICES>\n</DOCUMENT>'
        invoices = [Invoice(order,(i+1)+(n+1)+13000).to_xml() for i,order in enumerate(orders)]
        if ecm:
            path = rf'{drive}:\ECM\Polling\{stid}\IN\RECVD\Invoice.xml'
            with open(path, 'w') as file: 
                file.write(header + ''.join([s.replace('<?xml version="1.0" ?>','') for s in invoices]) + footer)
                print('receipts building in Retail Pro')
                os.system(fr'cd \ && {drive}: && cd ECM && ecmproc -a -in -stid:{stid}')
        else:
            with open('Invoice.xml', 'w') as file:
                file.write(header + ''.join([s.replace('<?xml version="1.0" ?>','') for s in invoices]) + footer)





#%%
