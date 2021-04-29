# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:29:51 2020

@author: Bagpyp
"""


# controls

clearanceIsOn = False
test = False
excluded_vendor_codes = []
excluded_dcs_codes = []

import datetime as dt
import json
a = dt.datetime.now()
print('began ',a.ctime())
from time import sleep, gmtime
import tools
from maps import to_clearance_map
from tqdm import tqdm
from numpy import where
import pandas as pd
pd.options.mode.chained_assignment=None
pd.options.display.max_rows = 150
pd.options.display.max_columns = 75
pd.options.display.width = 180
pd.options.display.max_colwidth = 30
from pprint import pprint
from picklist import picklist
from secretInfo import is_nighttime
from account import pull_invoices, pull_orders




#%% ORDERS

new_orders = tools.get_orders()
tools.document(new_orders)

w = pd.read_csv('invoices/written.csv')
new_returns = tools.get_returns()
tools.document([ret for ret in new_returns \
                if str(ret.get('id')) in \
                w.comment1.apply(lambda x: x.split(' ')[1]).tolist()], \
                   regular=False)


#%%

try: 
    picklist(local=False)
except Exception: 
    pass

#%% ECM
print('pulling data from ECM')

if test:
    df = tools.fromECM(run=False,ecm=False)
else:
    df = tools.fromECM()

    
#%%


df = df[(~df.VC.isin(excluded_vendor_codes))\
        &(~df.DCS.isin(excluded_dcs_codes))]

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

if clearanceIsOn:    
    # add clearance dataframe, clr to df
    df = pd.concat([df,clr]).sort_index()
    
# drop rental, service and used product (not clearance)
df = df[~df.DCS.str.match(r'(SER|REN|USD)')]

#map the rest of the categories, map null to Misc
df.CAT = df.CAT.map(tools.category_map).fillna('Misc')

# filters products without UPCs w/ length 11, 12 or 13.
if clearanceIsOn: 
    df = df[(df.UPC.str.len().isin([11,12,13]))|\
        (df.CAT.isin(clr.CAT))]
else:
    df = df[df.UPC.str.len().isin([11,12,13])]

# map null brands to Hillcrest
df.BRAND = df.BRAND.str.strip().str.replace('^$','Hillcrest', regex=True)

df.sku = df.sku.astype(int)
df = df.sort_values(by='sku')
df.sku = df.sku.astype(str).str.zfill(5)
df.set_index('sku', drop=True, inplace=True)
df = df[df['name'].notna()]
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
    print('pulling product data from BigCommerce')
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

print('reshaping media...')
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


#%% PULL ARCHIVE, BREAK IN TWO

df = pd.read_pickle('ready.pkl')

if test:
    print('runtime: ',dt.datetime.now()-a)
    
else:
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
    df['brand'] = df.BRAND.str.lower().map({v.lower():str(k) for k,v in b.items()})
    # not awseome yet, must create CAT
    df['cat'] = df.CAT.map({v:str(k) for k,v in c.items()})


    year = gmtime().tm_year
    month = gmtime().tm_mon
    # only showing last 3 years - (3)
    # winter product becomes old in May - (4)
    # summer product becomes old in November - (11)
    old = [f'{n-1}-{n}' for n in range(int(str((year+1)-3)[2:])+int(month>=5), \
                                    int(str(year)[2:])+int(month>=5))] \
        + [str(i) for i in range(int(str(year-3))+int(month>=5), \
                                int(year) + int(month>=11))]
    new = [f'{(int(str(year)[:2])-1) + int(month > 5)}' \
            + f'-{(int(str(year)[:2])) + int(month > 5)}',
            f'{year + int(month > 11)}']
        
    
    df['is_old'] = df.webName.str.contains('|'.join(old))
    df['clearance_cat'] = where(
        df.webName.str.contains('|'.join(old)),
        df.cat.map(to_clearance_map),
        ''
    )
    
    
    df = df[df.brand!='']
    
    gb = df.groupby('webName')


    new = gb.filter(lambda g: g.p_id.count()==0).groupby('webName',sort=False)
    old = gb.filter(lambda g: (\
                g.lModified.max()>(dt.datetime.now()-dt.timedelta(\
                                             days = tools.daysAgo+1))
                )\
            &(g.p_id.count()==1)).groupby('webName',sort=False)
        
    try: 
        picklist()
    except Exception: 
        pass

    
     
    #%% UPDATABLES
    

    # UPDATE
    updatables = []
    print('building payloads for update...')
    sleep(1)
    for _,g in tqdm(old):
        try:
            updatables.append(tools.upPayload(g))
        except:
            print('exception occured with \n')
            print(g)
            continue
        
    #%% UPDATE 

    updated = []
    updateFailed = []

    if len(updatables)>0:
        tools.log(f'updating {len(updatables)} products...', stamp=True)
        print(f'updating {len(updatables)} products...')
        sleep(1)
        for i,u in tqdm(enumerate(updatables)):
            # if i <= 71: continue
            uid = u.pop('id')
            try:
                res = tools.updateProduct(uid,u)
            except Exception:
                print(i,' connError')
                continue
            if all([r.ok for r in res]):
                updated.append(res)
            elif any([r.status_code==429 for r in res]):
                sleep(30)
                res = tools.updateProduct(uid,u, slow=True)
                if all([r.ok for r in res]):
                    updated.append(res)  
        
            else:
                tools.log(f"failed updatables[{i}], p_id={uid}\n{u}")
                # tools.deleteProduct(uid)
                updateFailed.append(res)



    #%% CREATABLES
    
    try: 
        picklist()
    except Exception: 
        pass



    creatables = []
    print('building payloads for creation...')
    # sleep(1)
    for _,g in tqdm(new):
        try:
            creatables.append(tools.newPayload(g))
        except:
            print(f'exception occured with {g.sku}\n')
            # print(g)
            continue

    created = []
    failed = []
    
    #%% CREATE

    """
    BROTEN
    """
    

    if len(creatables)>0:
    
        
        print('product creation iminent...')
        sleep(1)    
        tools.log('product creation status', stamp=True)

    for i,c in tqdm(enumerate(creatables)):
        res = tools.createProduct(c)
        if res.ok:
            created.append(res)
            # Add eBay product ID metafields w/ id & cat id
            p_id = str(res.json()['data']['id'])
            cat = str(res.json()['data']['categories'][0])
            if cat in tools.to_ebay_map:
                tools.createCustomField(
                        p_id,
                        'eBay Category ID',
                        cat
                    )
            else:
                tools.createCustomField(
                        p_id,
                        'eBay Category ID',
                        "0"
                    )
            
            tools.log(f"created {c['name']}")
        else:        
            failed.append(res)
            if json.loads(res.content)['title'] in ['The product name is a duplicate','Variant with the same option values set exists']:
                continue
            elif (json.loads(res.content)['title'] == "The field 'image_url' is invalid.") and ('images' in c):
                
                # have to remove image from media.pkl
                
                
                c.pop('images')
                if 'variants' in c:
                    for v in c['variants']:
                        if 'image_url' in v:
                            v.pop('image_url')
                c['is_visible'] = False
                res = tools.createProduct(c)
                if res.ok:
                    created.append(res)
                    # Add eBay product ID metafields w/ id & cat id
                    j = res.json()
                    p_id = str(j['data']['id'])
                    cat = str(j['data']['categories'][0])
                    sale_price = str(j['data']['sale_price'])
                    if cat in tools.to_ebay_map:
                        tools.createCustomField(
                                p_id,
                                'eBay Category ID',
                                cat
                            )
                        tools.createCustomField(
                                p_id,
                                'eBay Sale Price',
                                str(sale_price)
                            )
                    else:
                        tools.createCustomField(
                                p_id,
                                'eBay Category ID',
                                "0"
                            )
                        tools.createCustomField(
                                p_id,
                                'eBay Sale Price',
                                str(sale_price)
                            )
                    
                    tools.log(f"created {c['name']}")
            
            
            
            
            
            # tools.log(f"\t{c['name']} failed, trying again")
            # sleep(1)
            # res = tools.createProduct(c)
            # if not res.ok:
            #     tools.log(f"\t{c['name']} failed twice!")
            #     failed.append(res)
            # else:
            #     tools.log(f"\t\tcreated {c['name']} on 2nd attempt!")
            #     created.append(res)

    with open('productLog.txt','w') as f:
        f.write('[')
        for c in created:
            try:
                f.write(json.dumps(json.loads(c.content)))
            except:
                continue
            f.write(',')
        f.write(']')
        
    with open('failureLog.txt','w') as f:
        for i,d in enumerate(failed):
            f.write('\n')
            f.write('-'*100+f'\n\n{i}\n\n')
            try:
                pprint(json.loads(d.content),f)
            except:
                continue
            f.write('\n\n')
            pprint(json.loads(d.request.body),f)
            f.write('\n\n')
        


    #%%
    print('runtime: ',dt.datetime.now()-a)
    
    try: 
        picklist()
    except Exception: 
        pass

    if is_nighttime:
        pull_invoices()
        pull_invoices(test=True,clocks=True)
        pull_orders()