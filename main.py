# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:29:51 2020

@author: Bagpyp
"""

test = False

import datetime as dt
import json
a = dt.datetime.now()
from time import sleep
import tools
from tqdm import tqdm
import pandas as pd
pd.options.mode.chained_assignment=None
pd.options.display.max_rows = 150
pd.options.display.max_columns = 50
pd.options.display.width = 180
pd.options.display.max_colwidth = 30
from pprint import pprint

#%% ORDERS

tools.document(tools.newOrders())

#%% ECM
if test:
    df = tools.fromECM(run=False,ecm=False)
else:
    df = tools.fromECM()

# nuke duplicate SKUs
df = df[~df.sku.duplicated(keep=False)]

# just to make sure we have all the UPCs
df.UPC = df.UPC.fillna(df.UPC2)
df.drop(columns='UPC2', inplace=True)



# formatting columns
for i in range(12,18):
    df.iloc[:,i] = df.iloc[:,i].map(pd.to_numeric)

# bad solution
df.lModified = df.lModified.astype(str).str[:-6]
for i in range(18,23):
    df.iloc[:,i] = df.iloc[:,i].map(lambda x: \
        pd.to_datetime(x,format='%Y-%m-%dT%H:%M:%S'))

for i in range(23,29):
    df.iloc[:,i] = df.iloc[:,i].fillna('0').astype(int)\
        .map(lambda x: 0 if x < 0 else x)
        
# ATTN: setting qty to only store quantity (qty1)
df.qty = df.qty1
# keeing old DCS name
df['DCSname'] = df.CAT.values
#extract all positive qty used and renatl products
clr = df[df.DCS.str.match(r'(REN|USD)') & df.qty>0]
# remove USD and REN tags in DCS
clr.DCS = clr.DCS.str.replace('REN','').str.replace('USD','')
# map modified DCSs to above categories
clr.CAT = clr.DCS.map(tools.clearance_map)
# add clearance dataframe, clr to df
df = pd.concat([df,clr]).sort_index()
# drop rental, service and used product (not clearance)
df = df[~df.DCS.str.match(r'(SER|REN|USD)')]

#map the rest of the categories, map null to Misc
df.CAT = df.CAT.map(tools.category_map).fillna('Misc')

# filters products without UPCs w/ length 11, 12 or 13.
df = df[(df.UPC.str.len().isin([11,12,13]))|\
        (df.CAT.isin(clr.CAT))]

# map null brands to Hillcrest
df.BRAND = df.BRAND.replace('',tools.nan).fillna('Hillcrest').str.title()

df.sku = df.sku.astype(int)
df = df.sort_values(by='sku')
df.sku = df.sku.astype(str).str.zfill(5)
df.set_index('sku', drop=True, inplace=True)
df['webName'] = (df.name.str.title() + ' ' + df.year.fillna('')).str.strip()

# settling webNames with more than one ssid
chart = df[['webName','ssid']].groupby('ssid')\
    .first()\
    .sort_values(by='webName')
j = 0
for i in range(1, len(chart)):
    if chart.iloc[i,0]!=chart.iloc[i-(j+1),0]:
        j = 0
    else: 
        chart.iloc[i,0] += f' {j+1}'
        j+=1
df.webName = df.ssid.map(chart.webName.to_dict())

# options
df = tools.configureOptions(df)

#%% JOIN AND MEDIATE


df= df[['webName',
        'sku',
        'UPC',
        'CAT',
        'DCSname',
        'BRAND',
        'name',
        'mpn',
        'size',
        'color',
        'qty',
        'cost',
        'pSale',
        'pMAP',
        'pMSRP',
        'fCreated',
        'lModified',
        'description']]

if test:
    pdf = pd.read_pickle('products.pkl')
else:
    pdf = tools.updatedProducts().reset_index()

#should have no effect after problem is fixed
pdf.p_id = pdf.p_id.astype(int).astype(str)
pdf.v_id = pdf.v_id.astype(int).astype(str)
df = df[~df.sku.duplicated(keep=False)]

# LZ for 5 image columns
for i in range(5):
    if f'image_{i}' not in pdf:
        pdf[f'image_{i}'] = tools.nan


pdf = pdf[pdf.v_sku.replace('',tools.nan).notna()]\
    [['p_name',
    'p_sku',
    'v_sku',
    'p_categories',
    'p_description',
    'v_image_url',
    'p_is_visible',
    'p_date_created',
    'p_date_modified',
    'p_id',
    'v_id']+[f'image_{i}' for i in range(5)]]
    
df = pd.merge(df,pdf,how='left',left_on='sku',right_on='v_sku')\
    .replace('',tools.nan)

#reshape and archive images and descriptions

print('configuring product options...')
sleep(1)
df = tools.reshapeMedia(df)

print('archiving media...')
sleep(1)
# nuke duplicate SKUs
df = df[~df.sku.duplicated(keep=False)]

tools.archiveMedia(df)

#%% DELETE CONFLICT PRODUCTS
df = pd.read_pickle('mediatedDf.pkl')
nosync = df.groupby('webName').filter(lambda g: \
                        ((g.p_id.count() > 0)\
                        & (g[['p_id','v_id']].count().sum() < len(g))))
for id_ in nosync.p_id.dropna().unique().tolist():
    tools.deleteProduct(id_)

#problem
df = df.set_index('sku')
df.loc[nosync.sku.tolist(),['p_name',
                            'p_sku',
                            'v_sku',
                            'p_categories',
                            'p_description',
                            'v_image_url',
                            'p_is_visible',
                            'p_date_created',
                            'p_date_modified',
                            'p_id',
                            'v_id']] = tools.nan

df.to_pickle('ready.pkl')

if test:
    print('runtime: ',dt.datetime.now()-a)
    
else:

    #%% PULL ARCHIVE, BREAK IN TWO
    df = pd.read_pickle('ready.pkl')
    df.update(pd.read_pickle('media.pkl'))
    df = df.join(tools.fileDf())
    df.index.name = 'sku'
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

    b = tools.brandIDs()
    c = tools.categoryIDs()

    # awesome
    for brand in df[~df.BRAND.isin(list(b.values()))].BRAND.unique():
        b.update({tools.createBrand(brand):brand})
    df['brand'] = df.BRAND.map({v:str(k) for k,v in b.items()})
    # not awseome yet, must create CAT
    df['cat'] = df.CAT.map({v:str(k) for k,v in c.items()})

    gb = df.groupby('webName')


    new = gb.filter(lambda g: g.p_id.count()==0).groupby('webName',sort=False)
    old = gb.filter(lambda g: (\
                g.lModified.max()>(dt.datetime.now()-dt.timedelta(\
                                             days = tools.daysAgo+1))
                )\
            &(g.p_id.count()==1)).groupby('webName',sort=False)
     
    #%% UPDATE


    # UPDATE
    updatables = []
    print('building payloads for update...')
    sleep(1)
    for _,g in tqdm(old):
        updatables.append(tools.upPayload(g))

    updated = []
    updateFailed = []

    if len(updatables)>0:
        tools.log(f'updating {len(updatables)} products...', stamp=True)
        print(f'updating {len(updatables)} products...')
        sleep(1)
        for i,u in tqdm(enumerate(updatables)):
            uid = u.pop('id')
            res = tools.updateProduct(uid,u)
            if all([r.ok for r in res]):
                updated.append(res)
            else:
                tools.log(f"failure occured with productID {uid}")
                updateFailed.append(res)


    #%% CREATE


    creatables = []
    print('building payloads for creation...')
    sleep(1)
    for _,g in tqdm(new):
        creatables.append(tools.newPayload(g))

    created = []
    failed = []

    if len(creatables)>0:
        
        print('product creation iminent...')
        sleep(1)    
        tools.log('product creation status', stamp=True)

    for i,c in tqdm(enumerate(creatables)):
        res = tools.createProduct(c)
        if res.ok:
            created.append(res)
            tools.log(f"created {c['name']}")
        else:        
            tools.log(f"\t{c['name']} failed, trying again")
            sleep(1)
            res = tools.createProduct(c)
            if not res.ok:
                tools.log(f"\t{c['name']} failed twice!")
                failed.append(res)
            else:
                tools.log(f"\t\tcreated {c['name']} on 2nd attempt!")
                created.append(res)

    with open('productLog.txt','w') as f:
        f.write('[')
        for c in created:
            f.write(json.dumps(json.loads(c.content)))
            f.write(',')
        f.write(']')
        
    with open('failureLog.txt','w') as f:
        for i,d in enumerate(failed):
            f.write('\n')
            f.write('-'*100+f'\n\n{i}\n\n')
            pprint(json.loads(d.content),f)
            f.write('\n\n')
            pprint(json.loads(d.request.body),f)
            f.write('\n\n')
        
            
    print('runtime: ',dt.datetime.now()-a)
