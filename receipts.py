# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:02:30 2020

@author: Bagpyp
"""

import datetime as dt
from functools import reduce
from numpy import nan
import os
import pandas as pd
import requests
from secretInfo import headers,base,stid
import time

def getOrders(status_id=10,i=1):
    url = base + f'v2/orders?status_id={status_id}'\
        + f'&limit=50&page={i}'
    res = requests.get(url, headers = headers)
    if res.text:
        orders = res.json()       
        products = []
        shipping_addresses = [] 
        coupons = []
        for order in orders:
            res = requests.get(order['products']['url'],\
                                         headers = headers)
            if res.text:
                products.extend(res.json())
            res = requests.get(order['shipping_addresses']['url'],\
                                         headers = headers)
            if res.text:
                shipping_addresses.extend(res.json())
            res = requests.get(order['coupons']['url'],\
                                         headers = headers)
            if res.text:
                coupons.extend(res.json())
        o = pd.json_normalize(orders)
        if any(o):
            o['order_id']=o.id    
            p = pd.json_normalize(products)
            c = pd.json_normalize(coupons)
            a = pd.json_normalize(shipping_addresses)
            if not any(c):
                c[['id','order_id','code','coupon_id','discount']]=nan
            df = reduce(lambda x,y: pd.merge(x,y,\
                                             how='outer',\
                                             on='order_id',\
                                             copy=False),\
                        [x.drop('id',axis=1) for x in [o,p,c,a]])
            df = df[['order_id',
                      'date_created',
                      'date_modified',
                      'status_id',
                      'status',
                      'subtotal_inc_tax',
                      'total_inc_tax_x',
                      'items_total_x',
                      'payment_method',
                      'payment_provider_id',
                      'payment_status',
                      'refunded_amount',
                      'product_id',
                      'variant_id',
                      'order_address_id',
                      'name',
                      'sku',
                      'upc',
                      'base_price',
                      'price_inc_tax',
                      'base_total',
                      'quantity',
                      'base_cost_price',
                      'cost_price_inc_tax',
                      'is_refunded',
                      'quantity_refunded',
                      'refund_amount',
                      'coupon_id',
                      'code',
                      'discount',
                      'first_name',
                      'last_name',
                      'street_1',
                      'street_2',
                      'city',
                      'zip',
                      'country',
                      'state',
                      'email',
                      'phone',
                      'base_cost']]
            return df
def countOrders(status_id=10):
    url = base + 'v2/orders/count'
    res = requests.get(url,headers = headers)
    oc = res.json()['statuses']
    return oc[['id' in x and x['id']==status_id for x in oc]\
       .index(True)]['count']
def allOrders(pickled_orders,status_id=10):
    ordersUp = countOrders(status_id)
    num_pickled_orders = len(pickled_orders.order_id.unique())
    if ordersUp > num_pickled_orders:
        print('orders found on BigCommerce, pulling...')
        dfs = []
        for n in range((countOrders(status_id)//50)+1):
            dfs.append(getOrders(i=n+1))
        return pd.concat(dfs,ignore_index=True)
    else:
        return pickled_orders
# RERUN IF PKL LOST
# orders = allOrders(10)
# orders.to_pickle('orders.pkl')
def newOrders():
    pickled_orders = pd.read_pickle('orders.pkl')
    orders = allOrders(pickled_orders)
    orders.to_pickle('orders.pkl')
    if len(orders) > len(pickled_orders):
        return orders[~orders.order_id.isin(pickled_orders.order_id)]
    else:
        print('no new orders found, make sure status is changed to',
              '`Completed` in BigCommerce Admin Panel')
        return pd.DataFrame(columns=pickled_orders.columns.tolist())
        
 
# ecm in

def writeInvoice(df, ecm=True, drive='E', stid = stid):
    archive = pd.read_pickle('orders.pkl')
    
    ecmDf = pd.read_pickle('fromECM.pkl')
    df['ecmSKU'] = df.sku.str[2:].str.lstrip('0')
    df.discount = df.discount.fillna(0)
    df = pd.merge(df,ecmDf,left_on='ecmSKU',right_on='sku',\
                  suffixes=('_bc','_rp')).set_index('order_id')
    
    beginning = dt.datetime.now()
    now = str(beginning).replace(" ","T").split('.')[0]
    def item(oid,j,invc_sid):
        row = df.loc[[oid]].iloc[j]
        s = f"""\t\t\t\t<INVC_ITEM invc_sid="{invc_sid}"
                        item_pos="{j+1}" 
                        item_sid="{row.isid}" 
                        qty="{row.quantity}" 
                        orig_price="{row.pSale}" 
                        orig_tax_amt="0" 
                        price="{round(float(row.subtotal_inc_tax)-float(row.discount),2)}" 
                        cost="{row.cost_price_inc_tax}" 
                        price_lvl="1" 
                        empl_sbs_no="1" 
                        empl_name="Robbie">
                        <INVN_BASE_ITEM item_sid="{row.isid}" 
                            flag="0" 
                            ext_flag="0" />
                    </INVC_ITEM>
    """
        return s
    
    def invoice(oid, num):
        row = df.loc[[oid]].iloc[0]
        invc_sid = int(str(101000)+str(id(dt.datetime.now())))
        time.sleep(1)
        cust_sid = int(str(101000)+str(id(dt.datetime.now())))
        s =f"""\t\t<INVOICE invc_sid="{invc_sid}"
                sbs_no="1" 
                store_no="1" 
                invc_no="{12000+len(archive)+num}"
                invc_type="0" 
                status="2" 
                proc_status="3" 
                cust_sid="5274779657848317680"  
                rounding_offset="0" 
                created_date="{now}" 
                modified_date="{now}" 
                post_date="{now}" 
                tracking_no="" 
                cms_post_date="{now}" 
                ws_seq_no="29866" 
                held="0" 
                controller="0" 
                orig_controller="0" 
                empl_sbs_no="1" 
                empl_name="Robbie" 
                createdby_sbs_no="1" 
                createdby_empl_name="Robbie">
                <CUSTOMER cust_sid="5274779657848317680" 
                    cust_id="38342" 
                    store_no="0" 
                    modified_date="{now}" 
                    sbs_no="1" 
                    cms="3" />
                <SHIPTO_CUSTOMER cust_sid="{cust_sid}"
                    cust_id="{str(200000+len(archive)+num)}"
                    store_no="1"
                    first_name="{row.first_name}"
                    last_name="{row.last_name}"
                    price_lvl=""
                    modified_date="{now}"
                    sbs_no="1"
                    cms="0"
                    company_name=""
                    title=""
                    tax_area_name=""
                    shipping="1"
                    address1="{row.street_1}"
                    address2="{row.street_2}"
                    address3="{row.city + ', ' + row.state}"
                    email_addr="{row.email}"
                    zip="{row.zip}"
                    phone1="{row.phone}"
                    phone2=""
                    country_name="{row.country}"
                    alternate_id1=""
                    alternate_id2="" />
                <INVC_SUPPLS>
                    <INVC_SUPPL udf_no="1" 
                        udf_value="Walkby"/>
                </INVC_SUPPLS>
                <INVC_COMMENTS>
                    <INVC_COMMENT comment_no="1" 
                        comments="{'BC ' + str(row.name)}"/>
                    <INVC_COMMENT comment_no="2"
                        comments="{row.payment_provider_id}"/>
                </INVC_COMMENTS>
                <INVC_FEES>
                    <INVC_FEE fee_name="" 
                        fee_type="9"
                        amt="{row.base_cost}"/>
                </INVC_FEES>
                <INVC_TENDERS>
                    <INVC_TENDER tender_type="4" 
                        tender_no="1" 
                        given="0" 
                        amt="{row.total_inc_tax_x}"/>
                </INVC_TENDERS>
                <INVC_ITEMS>
    """
        for j in range(len(df.loc[[oid]])):
            s += item(oid,j,invc_sid)
        s += """\t\t\t</INVC_ITEMS>
            </INVOICE>
    """
        return s
            
    def document(df):
        s = """<?xml version="1.0" encoding="UTF-8"?>
    <DOCUMENT>
        <INVOICES>
    """
        for num, oid in enumerate(df.index.unique().tolist()):
            s += invoice(oid, num)
            time.sleep(1) # to reset id(())
        s += """\t</INVOICES>
    </DOCUMENT>
    """
        # s.replace
        return s.replace('nan','')
    
    print('writing XML for new orders...')
    # path = f"test/Invoice {str(dt.datetime.now().date())+str(dt.datetime.now().time())[:5].replace(':','_')}.xml"
    path = rf'{drive}:\ECM\Polling\{stid}\IN\RECVD\Invoice.xml'
    with open(path, 'w') as file: 
        file.write(document(df))
        
    if ecm:
        print('receipts building in Retail Pro')
        os.system(f'{drive}: && cd ECM && ecmproc -a -in -stid:{stid}')
    