# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 13:02:38 2020

@author: Web
"""

import datetime as dt
a = dt.datetime.now()
import time

import tools
import pandas as pd
pd.options.mode.chained_assignment=None
pd.options.display.max_rows = 150
pd.options.display.max_columns = 50
pd.options.display.width = 200
pd.options.display.max_colwidth = 30

import tqdm
import requests
from numpy import nan

headers = {
'x-auth-client': "eptlgcc4vesdj5jp2as53w2gm6iyg7z",
'x-auth-token': "hugdph8qf3qa4haq5t1lewytanr5dwm",
'accept': 'application/json'
} # access tokens    
base = 'https://api.bigcommerce.com/stores/9hdarxbna5/'

# to get empty cats
# upliad this file and then delete all the products
# if you don't have the file, run this little fucker.

# with open('cat_backup.txt') as f:
#     cats = f.read()
# cats = list(set(cats.split('\n')))
# test = pd.DataFrame(columns = ['weight',
#                                'name',
#                                'price',
#                                'cat',
#                                'track'])
# for i,cat in enumerate(cats):
#     test = test.append({'name':f'test_{i}','cat':cat},ignore_index=True)
# test.weight = 0
# test.price = 10
# test.track = 'none'
    
# test.to_csv('cat import.csv')

def iterCall(call,*args):
    res = call(*args)
    if res.ok:
        j = res.json()
        data = j['data']
        pag = j['meta']['pagination']
        for i in tqdm.tqdm(range(2,pag['total_pages']+1)):
            data.extend(call(*args,i).json()['data'])
        return data
    
def brandIDs():
    def getBrands(i=1):
        url = base + 'v3/catalog/brands'\
            + f'?limit=50&page={i}'
        res = requests.get(url, headers=headers)
        return res
    data = iterCall(getBrands)
    return {d['id']:d['name'] for d in data}
def createBrand(name):
    """ returns brand ID upon creation"""
    url = base + 'v3/catalog/brands'
    h = headers.copy()
    h.update({'content-type':'application/json',
              'accept':'application/json'})
    d = {'name':f'{name}'}
    res = requests.post(url,headers=h,json=d)
    if res.ok:
        return res.json()['data']['id']
    


# categories

def categoryIDs():
    url = base + 'v3/catalog/categories/tree'
    res = requests.get(url,headers=headers)
    cat = {}
    for i in res.json()['data']:
        cat.update({i['id']:i['name']})
        for j in i['children']:
            cat.update({j['id']:i['name']+'/'+j['name']})
            for k in j['children']:
                cat.update({k['id']:i['name']+'/'+j['name']+'/'+k['name']})
    return cat
    
df = pd.read_pickle('ready.pkl')
df.update(pd.read_pickle('media.pkl'))
df = df.join(tools.fileDf())
df = df.reset_index()

#fill nulls with native zeros
df.loc[:,['p_id','v_id','v_image_url','image_0']] = \
    df[['p_id','v_id','v_image_url','image_0']].fillna('')   
df.loc[:,df.select_dtypes(object).columns.tolist()] = \
    df.select_dtypes(object).fillna('')
df.loc[:,df.select_dtypes(int).columns.tolist()] = \
    df.select_dtypes(int).fillna(0)
df.loc[:,df.select_dtypes(float).columns.tolist()] = \
    df.select_dtypes(float).fillna(0)
df.loc[:,['p_id','v_id','v_image_url','image_0']] = \
    df[['p_id','v_id','v_image_url','image_0']].replace('',tools.nan)    

b = brandIDs()
c = categoryIDs()

# awesome
print('creating brands')
for brand in tqdm.tqdm(df[~df.BRAND.isin(list(b.values()))].BRAND.unique()):
    b.update({createBrand(brand):brand})
    
    
df['brand'] = df.BRAND.map({v:str(k) for k,v in b.items()})
# not awseome yet, must create CAT
df['cat'] = df.CAT.map({v:str(k) for k,v in c.items()})
  


df[['p_id','v_id']] = nan
gb = df.groupby('webName')


new = gb.filter(lambda g: g.p_id.count()==0).groupby('webName',sort=False)
old = gb.filter(lambda g: (\
            g.lModified.max()>(dt.datetime.now()-dt.timedelta(\
                                         days = tools.daysAgo+1))
            )\
        &(g.p_id.count()==1)).groupby('webName',sort=False)
 


        





def createProduct(data):
    url = base + 'v3/catalog/products'
    h = headers.copy()
    h.update({'content-type':'application/json'})
    res = requests.post(url,headers = h,json=data)
    return res



def newPayload(g):
    product = {}
    g = g.fillna('').to_dict('records')
    r = g[0]
    product.update({\
                'type':'physical',
                'weight':0,
                'categories':[int(r['cat'])],
                'brand_id':int(r['brand']),
                'name':r['webName'],
                'sale_price':r['pSale'],
                'price':r['pMAP'],
                'retail_price':r['pMSRP'],
                'sku':r['sku'],
                'description':r['description'],
                })
    if r['image_0_file']!='':
        product.update({'is_visible':True})
        hasImages = 1
    elif r['image_0_file']=='':
        product.update({'is_visible':False})
        hasImages = 0
    if hasImages:
        product.update({\
                'images':\
                    [{'image_file':r['image_0_file'],\
                     'is_thumbnail': True}] + \
                    [{'image_file':r[f'image_{i}_file']} \
                    for i in range(1,5) if r[f'image_{i}_file'] !='']
                })
    if len(g)>1:
        product.update({\
                    'inventory_tracking':'variant'
                    })
        variants = []
        for h in g[1:]:
            variant = {}
            variant.update({\
                        'inventory_level':h['qty'],
                        'sale_price':h['pSale'],
                        'price':h['pMAP'],
                        'retail_price':h['pMSRP'],
                        'upc':h['UPC'],
                        'sku':h['sku'],
                        'mpn':h['mpn'],
                        'option_values':\
                            [{'option_display_name':s.title(),\
                              'label':h[s]} \
                                     if h[s]!='' \
                                     else \
                                         {'option_display_name':s.title(),\
                                          'label':'IRRELEVANT'}
                                     for s in ['color','size']]
                        })
            
            if h['v_image_url_file'] != '':
                variant.update({'image_file':h['v_image_url_file']})
            variants.append(variant)
        product.update({'variants':variants})
    elif len(g)==1:
        product.update({\
                    'inventory_tracking':'product',
                    'inventory_level':r['qty'],
                    'sale_price':r['pSale'],
                    'price':r['pMAP'],
                    'retail_price':r['pMSRP'],    
                    'mpn':r['mpn'],
                    'upc':r['UPC'],
                    'custom_fields':\
                        [{'name':s.title(),\
                          'value':r[s]} \
                                 for s in ['color','size']\
                                 if r[s]!='']
                    })
    return product
    
def newPayloadURL(g):
    product = {}
    g = g.fillna('').to_dict('records')
    r = g[0]
    product.update({\
                'type':'physical',
                'weight':0,
                'categories':[int(r['cat'])],
                'brand_id':int(r['brand']),
                'name':r['webName'],
                'sale_price':r['pSale'],
                'price':r['pMAP'],
                'retail_price':r['pMSRP'],
                'sku':r['sku'],
                'description':r['description'],
                })
    if r['image_0']!='':
        product.update({'is_visible':True})
        hasImages = 1
    elif r['image_0']=='':
        product.update({'is_visible':False})
        hasImages = 0
    for i in range(1,5):
        if r[f'image_{i}'] != '':\
            hasImages+=1
    if hasImages:
        product.update({\
                'images':\
                    [{'image_url':r['image_0'],\
                     'is_thumbnail': True}] + \
                    [{'image_url':r[f'image_{i}']} \
                    for i in range(1,5) if r[f'image_{i}'] !='']
                })
    if len(g)>1:
        product.update({\
                    'inventory_tracking':'variant'
                    })
        variants = []
        for h in g[1:]:
            variant = {}
            variant.update({\
                        'inventory_level':h['qty'],
                        'sale_price':h['pSale'],
                        'price':h['pMAP'],
                        'retail_price':h['pMSRP'],
                        'upc':h['UPC'],
                        'sku':h['sku'],
                        'mpn':h['mpn'],
                        'option_values':\
                            [{'option_display_name':s.title(),\
                              'label':h[s]} \
                                     if h[s]!='' \
                                     else \
                                         {'option_display_name':s.title(),\
                                          'label':'IRRELEVANT'}
                                     for s in ['color','size']]
                        })
            
            if h['v_image_url'] != '':
                variant.update({'image_url':h['v_image_url']})
            variants.append(variant)
        product.update({'variants':variants})
    elif len(g)==1:
        product.update({\
                    'inventory_tracking':'product',
                    'inventory_level':r['qty'],
                    'sale_price':r['pSale'],
                    'price':r['pMAP'],
                    'retail_price':r['pMSRP'],    
                    'mpn':r['mpn'],
                    'upc':r['UPC'],
                    'custom_fields':\
                        [{'name':s.title(),\
                          'value':r[s]} \
                                 for s in ['color','size']\
                                 if r[s]!='']
                    })
    return product



creatables = []
creatablesURL = []
i = 0
print('building payloads')
for _,g in tqdm.tqdm(new):
    # creatables.append(newPayload(g))
    creatablesURL.append(newPayloadURL(g))


#%%

created = []
firstResponse = []
secondCreate = []
failures = []
         
for i,c in enumerate(creatablesURL):

    print(f"creating {c['name']}")
    res = createProduct(c)
    if res.ok:
        created.append(res)
    else:
        time.sleep(1)
        firstResponse.append(res)
        res = createProduct(c)
        print('\t','trying this one again')
        secondCreate.append(res)
        if not res.ok:
            print(f'\t\tcreatables[{i}] failed')
            failures.append(c)
    break
