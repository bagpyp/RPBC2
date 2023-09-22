# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:29:51 2020

@author: Bagpyp
"""
from api import (
    updatedProducts,
    deleteProduct,
    brandIDs,
    categoryIDs,
    createBrand,
    updateProduct,
    updateCustomField,
    createProduct,
    retry,
    getProductBySku,
    getProductByName,
    createCustomField,
)
from media import configureOptions, reshapeMedia, archiveMedia, fileDf
from orders import get_orders
from out import fromECM
from payloads import upPayload, newPayload
from receipts import document
from returns import get_returns

# controls

clearanceIsOn = False
test = False
excluded_vendor_codes = []
excluded_dcs_codes = []

import datetime as dt

a = dt.datetime.now()
print("began ", a.ctime())
from time import sleep, gmtime
from maps import to_clearance_map, clearance_map, category_map, to_ebay_map
from tqdm import tqdm
from numpy import where, nan
import pandas as pd
from secret_info import is_nighttime, daysAgo
from account import pull_invoices, pull_orders
from quivers import send_to_quivers

"""TO ADD CHANNELS!!!"""
# customer and employee data has to go into MAPS.PY
# good luck bitch!!!

# taxes in walmart shouldn't be in receipt in rp
# comment 1 needs to be WAL <num>
# comment 2 needs to be


# %% ORDERS

new_orders = get_orders()
document(new_orders)

# %%

w = pd.read_csv("invoices/written.csv")
new_returns = get_returns()
document(
    [
        ret
        for ret in new_returns
        if str(ret.get("id")) in w.comment1.apply(lambda x: x.split(" ")[1]).tolist()
    ],
    regular=False,
)

# %% ECM
print("pulling data from ECM")

if test:
    df = fromECM(run=False, ecm=False)
else:
    df = fromECM()

# %%


df = df[(~df.VC.isin(excluded_vendor_codes)) & (~df.DCS.isin(excluded_dcs_codes))]

# nuke duplicate SKUs
df = df[~df.sku.duplicated(keep=False)]

# just to make sure we have all the UPCs
df.UPC = df.UPC.fillna(df.UPC2)
df.drop(columns="UPC2", inplace=True)

# formatting columns
for i in range(12, 18):
    df.iloc[:, i] = df.iloc[:, i].map(pd.to_numeric)

# bad solution
df.lModified = df.lModified.astype(str).str[:-6]
for i in range(18, 23):
    df.iloc[:, i] = df.iloc[:, i].map(
        lambda x: pd.to_datetime(x, format="%Y-%m-%dT%H:%M:%S")
    )

for i in range(23, 29):
    df.iloc[:, i] = (
        df.iloc[:, i].fillna("0").astype(int).map(lambda x: 0 if x < 0 else x)
    )

# ATTN: setting qty to only store quantity (qty1)
df.qty = df.qty1
# keeing old DCS name
df["DCSname"] = df.CAT.values
# extract all positive qty used and renatl products
clr = df[df.DCS.str.match(r"(REN|USD)") & df.qty > 0]
# remove USD and REN tags in DCS
clr.DCS = clr.DCS.str.replace("REN", "").str.replace("USD", "")
# map modified DCSs to above categories
clr.CAT = clr.DCS.map(clearance_map)

if clearanceIsOn:
    # add clearance dataframe, clr to df
    df = pd.concat([df, clr]).sort_index()

# drop rental, service and used product (not clearance)
df = df[~df.DCS.str.match(r"(SER|REN|USD)")]

# map the rest of the categories, map null to Misc
df.CAT = df.CAT.map(category_map).fillna("Misc")

# filters products without UPCs w/ length 11, 12 or 13.
if clearanceIsOn:
    df = df[(df.UPC.str.len().isin([11, 12, 13])) | (df.CAT.isin(clr.CAT))]
else:
    df = df[df.UPC.str.len().isin([11, 12, 13])]

# map null brands to Hillcrest
df.BRAND = df.BRAND.str.strip().str.replace("^$", "Hillcrest", regex=True)

df.sku = df.sku.astype(int)
df = df.sort_values(by="sku")
df.sku = df.sku.astype(str).str.zfill(5)
df.set_index("sku", drop=True, inplace=True)
df = df[df["name"].notna()]
df["webName"] = (df.name.str.title() + " " + df.year.fillna("")).str.strip()

# settling webNames with more than one ssid
chart = df[["webName", "ssid"]].groupby("ssid").first().sort_values(by="webName")
j = 0
for i in range(1, len(chart)):
    if chart.iloc[i, 0] != chart.iloc[i - (j + 1), 0]:
        j = 0
    else:
        chart.iloc[i, 0] += f" {j + 1}"
        j += 1
df.webName = df.ssid.map(chart.webName.to_dict())

# options
df = configureOptions(df)

# %% JOIN AND MEDIATE


df = df[
    [
        "webName",
        "sku",
        "UPC",
        "CAT",
        "DCSname",
        "BRAND",
        "name",
        "mpn",
        "size",
        "color",
        "qty",
        "cost",
        "pSale",
        "pMAP",
        "pMSRP",
        "pAmazon",
        "fCreated",
        "lModified",
        "description",
    ]
]

if test:
    pdf = pd.read_pickle("data/products.pkl")
else:
    print("pulling product data from BigCommerce")
    pdf = updatedProducts().reset_index()

# should have no effect after problem is fixed
pdf.p_id = pdf.p_id.astype(int).astype(str)
pdf.v_id = pdf.v_id.astype(int).astype(str)
df = df[~df.sku.duplicated(keep=False)]

# LZ for 5 image columns
for i in range(5):
    if f"image_{i}" not in pdf:
        pdf[f"image_{i}"] = nan

pdf = pdf[pdf.v_sku.replace("", nan).notna()][
    [
        "p_name",
        "p_sku",
        "v_sku",
        "p_categories",
        "p_description",
        "v_image_url",
        "p_is_visible",
        "p_date_created",
        "p_date_modified",
        "p_id",
        "v_id",
    ]
    + [f"image_{i}" for i in range(5)]
]

df = pd.merge(df, pdf, how="left", left_on="sku", right_on="v_sku").replace("", nan)

# reshape and archive images and descriptions

print("reshaping media...")
sleep(1)
df = reshapeMedia(df)

print("archiving media...")
sleep(1)
# nuke duplicate SKUs
df = df[~df.sku.duplicated(keep=False)]

archiveMedia(df)

# %% DELETE CONFLICT PRODUCTS
df = pd.read_pickle("data/mediatedDf.pkl")
nosync = df.groupby("webName").filter(
    lambda g: ((g.p_id.count() > 0) & (g[["p_id", "v_id"]].count().sum() < len(g)))
)

for id_ in nosync.p_id.dropna().unique().tolist():
    deleteProduct(id_)

# problem
df = df.set_index("sku")
df.loc[
    nosync.sku.tolist(),
    [
        "p_name",
        "p_sku",
        "v_sku",
        "p_categories",
        "p_description",
        "v_image_url",
        "p_is_visible",
        "p_date_created",
        "p_date_modified",
        "p_id",
        "v_id",
    ],
] = nan

df.to_pickle("ready.pkl")

# %% PULL ARCHIVE, BREAK IN TWO

df = pd.read_pickle("data/ready.pkl")

if test:
    print("runtime: ", dt.datetime.now() - a)

else:
    df = pd.read_pickle("data/ready.pkl")
    df.update(pd.read_pickle("data/media.pkl"))
    df = df.join(fileDf())
    df.index.name = "sku"
    df = df.reset_index()

    # fill nulls with native zeros
    df.loc[:, ["p_id", "v_id", "v_image_url", "image_0"]] = df[
        ["p_id", "v_id", "v_image_url", "image_0"]
    ].fillna("")
    df.loc[:, df.select_dtypes(object).columns.tolist()] = df.select_dtypes(
        object
    ).fillna("")
    df.loc[:, df.select_dtypes(int).columns.tolist()] = df.select_dtypes(int).fillna(0)
    df.loc[:, df.select_dtypes(float).columns.tolist()] = df.select_dtypes(
        float
    ).fillna(0)
    df.loc[:, ["p_id", "v_id", "v_image_url", "image_0"]] = df[
        ["p_id", "v_id", "v_image_url", "image_0"]
    ].replace("", nan)

    b = brandIDs()
    c = categoryIDs()

    # awesome
    for brand in df[~df.BRAND.isin(list(b.values()))].BRAND.unique():
        b.update({createBrand(brand): brand})
    df["brand"] = df.BRAND.str.lower().map({v.lower(): str(k) for k, v in b.items()})
    # not awseome yet, must create CAT
    df["cat"] = df.CAT.map({v: str(k) for k, v in c.items()})

    year = gmtime().tm_year
    month = gmtime().tm_mon
    # only showing last 3 years - (3)
    # winter product becomes old in May - (4)
    # summer product becomes old in November - (11)
    old = [
        f"{n - 1}-{n}"
        for n in range(
            int(str((year + 1) - 3)[2:]) + int(month >= 5),
            int(str(year)[2:]) + int(month >= 5),
        )
    ] + [
        str(i)
        for i in range(
            int(str(year - 3)) + int(month >= 5), int(year) + int(month >= 11)
        )
    ]
    new = [
        f"{(int(str(year)[-2:]) - 1) + int(month > 5)}"
        + f"-{(int(str(year)[-2:])) + int(month > 5)}",
        f"{year + int(month > 11)}",
    ]

    df["is_old"] = df.webName.str.contains("|".join(old))
    df["clearance_cat"] = where(
        df.webName.str.contains("|".join(old)), df.cat.map(to_clearance_map), ""
    )

    df = df[df.brand != ""]

    df.pAmazon = df.pAmazon.round(2)

    gb = df.groupby("webName")

    new = gb.filter(lambda g: g.p_id.count() == 0).groupby("webName", sort=False)
    old = gb.filter(
        lambda g: (
            g.lModified.max() > (dt.datetime.now() - dt.timedelta(days=daysAgo + 1))
        )
        & (g.p_id.count() == 1)
    ).groupby("webName", sort=False)

    # %% UPDATABLES

    # UPDATE
    updatables = []
    print("building payloads for update...")
    sleep(1)
    for _, g in tqdm(old):
        try:
            updatables.append(upPayload(g))
        except:
            print("exception occurred with \n")
            print(g)
            continue

    # %% UPDATE

    updated = []
    updateFailed = []

    if len(updatables) > 0:
        print(f"updating {len(updatables)} products...")
        sleep(1)
        for i, u in tqdm(enumerate(updatables)):
            uid = u.pop("id")
            try:
                res = updateProduct(uid, u)
                updateCustomField(uid, "eBay Sale Price", u["amazon_price"])
            except Exception:
                print(i, " connError")
                updateFailed.append((uid, res))
                continue
            if all([r.ok for r in res]):
                updated.append(res)
            elif any([r.status_code == 429 for r in res]):
                sleep(30)
                res = updateProduct(uid, u, slow=True)
                updateCustomField(uid, "eBay Sale Price", u["amazon_price"])
                if all([r.ok for r in res]):
                    updated.append(res)

            else:
                # deleteProduct(uid)
                updateFailed.append(res)

    # %%

    creatables = []
    print("building payloads for creation...")
    # sleep(1)
    for _, g in tqdm(new):
        try:
            creatables.append(newPayload(g))
        except:
            print(f"exception occured with {g.sku}\n")
            # print(g)
            continue

    # %% CREATE

    created = []
    failed = []

    if len(creatables) > 0:
        print("product creation imminent...")
        sleep(1)

    for i, c in tqdm(enumerate(creatables)):
        try:
            res = createProduct(c)
            if not res.ok:
                if res.reason == "Too Many Requests" or res.status_code == 429:
                    try:
                        sleep(int(res.headers["X-Rate-Limit-Time-Reset-Ms"]) / 1000)
                    except KeyError:
                        sleep(
                            int(res.headers["X-Rate-Limit-Time-Reset-Ms".lower()])
                            / 1000
                        )
                        res = retry(res)
                if res.reason == "Conflict":
                    if "product sku is a duplicate" in res.text:
                        conflict_sku = c["sku"]
                        conflict_products = getProductBySku(conflict_sku).json()["data"]
                        for cp in conflict_products:
                            deleteProduct(cp["id"])
                        res = retry(res)
                    if "product name is a duplicate" in res.text:
                        conflict_name = c["name"]
                        conflict_products = getProductByName(conflict_name).json()[
                            "data"
                        ]
                        for cp in conflict_products:
                            deleteProduct(cp["id"])
                        res = retry(res)
                if (
                    "could not be processed and may not be valid image" in res.text
                    or "could not be downloaded and may be invalid"
                ):
                    # TODO! have to remove image from media.pkl ???
                    # otherwise products will keep being set to visible when they
                    # shouldn't be
                    # call Robbie 5038034458 and say "you're retrying priduct
                    # creation even though the images can't get processed in
                    # BigCommerce.  the media pickle has a record of that image so
                    # it's gtting set to visible...

                    if "images" in c:
                        c.pop("images")
                    if "variants" in c:
                        for v in c["variants"]:
                            if "image_url" in v:
                                v.pop("image_url")
                    c["is_visible"] = False
                    res = createProduct(c)
            if res.ok:
                created.append(res)
                j = res.json()["data"]
                # Add eBay product ID metafields w/ id & cat id
                p_id = str(j["id"])
                # add amazon price to custom field
                updateCustomField(p_id, "eBay Sale Price", c["amazon_price"])
                cat = str(j["categories"][0])
                sale_price = str(j["sale_price"])
                if cat in to_ebay_map:
                    createCustomField(p_id, "eBay Category ID", cat)
                else:
                    createCustomField(p_id, "eBay Category ID", "0")

            else:
                failed.append(res)

        except Exception:
            continue

    # %%
    print("runtime: ", dt.datetime.now() - a)

    try:
        send_to_quivers()
    except Exception:
        pass

    if is_nighttime:
        pull_invoices()
        pull_orders()
