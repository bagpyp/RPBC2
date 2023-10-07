# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:29:51 2020

@author: Bagpyp
"""
import datetime as dt
import json
import re
from time import sleep, gmtime

import pandas as pd
from numpy import where, nan
from tqdm import tqdm

from media import configureOptions, reshapeMedia, archiveMedia, fileDf
from orders import get_all_orders, get_all_returns
from out import fromECM
from payloads import product_update_payload, product_creation_payload
from quivers import send_to_quivers
from receipts import document
from secret_info import daysAgo
from src.api import (
    delete_product,
    get_all_brand_ids,
    get_all_category_ids,
    create_brand,
    update_product,
    update_custom_field,
    create_product,
    updated_products,
    get_product_by_sku,
    get_product_by_name,
    retry_request_using_response,
)
from src.data_maps import (
    category_map,
    clearance_map,
    to_clearance_map,
    to_ebay_map,
)
from util.path_utils import DATA_DIR, LOGS_DIR

fast = False
clearanceIsOn = False
excluded_vendor_codes = []
excluded_dcs_codes = []
amazon_excluded_vendors = [
    "686",
    "Arbor Snowboards",
    "Arcade Belts",
    "Bronson Speed Co.",
    "Bullet",
    "Burton",
    "Capita",
    "Crab Grab",
    "Creature",
    "Darn Tough",
    "Gnu",
    "Havaianas",
    "Helly Hansen",
    "Hestra",
    "Hot Chillys",
    "Hydro Flask",
    "Independent",
    "Lib Technologies",
    "Marmot",
    "Nike",
    "Nikwax",
    "OJ Iii",
    "PIT VIPER",
    "Picture Organic Clothing",
    "RVCA",
    "Reef",
    "Ricta",
    "Salomon Ski",
    "Santa Cruz",
    "Smartwool",
    "Smith",
    "Spyder Active Sports",
    "Stance",
    "Sun Bum",
    "The North Face",
    "Theragun",
    "Turtle Fur",
    "Under Armour",
    "Union Binding Company",
    "Vans",
    "Wolfgang",
]

a = dt.datetime.now()
print(f"Began {a}, processing changes in RetailPro over the last {daysAgo} days...")

# %% ORDERS AND RETURNS

if not fast:
    new_orders = get_all_orders()
    document(new_orders)

    w = pd.read_csv("invoices/written.csv")
    new_returns = get_all_returns()
    document(
        [
            ret
            for ret in new_returns
            if str(ret.get("id"))
            in w.comment1.apply(lambda x: x.split(" ")[1]).tolist()
        ],
        regular=False,
    )

# %% ECM

if fast:
    df = fromECM(run=False, ecm=False)
else:
    print("Pulling data from ECM on the server via PROC OUT")
    df = fromECM()

# %% TRANSFORM
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
# keeping old DCS name
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

# %%  PRODUCT OPTIONS

df = configureOptions(df)

# %%  JOIN AND MEDIATE

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

if fast:
    pdf = pd.read_pickle(f"{DATA_DIR}/products.pkl")
else:
    print("pulling product data from BigCommerce")
    pdf = updated_products().reset_index()

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


df = reshapeMedia(df)

print("Archiving new images from BigCommerce")
sleep(1)
# nuke duplicate SKUs
df = df[~df.sku.duplicated(keep=False)]

archiveMedia(df)

# %% DELETE CONFLICT PRODUCTS
df = pd.read_pickle(f"{DATA_DIR}/mediatedDf.pkl")
nosync = df.groupby("webName").filter(
    lambda g: ((g.p_id.count() > 0) & (g[["p_id", "v_id"]].count().sum() < len(g)))
)

for id_ in nosync.p_id.dropna().unique().tolist():
    delete_product(id_)

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

mdf = pd.read_pickle(f"{DATA_DIR}/media.pkl")
df.update(mdf)
df = df.join(fileDf())
df.index.name = "sku"
df = df.reset_index()

# fill nulls with native zeros
df.loc[:, ["p_id", "v_id", "v_image_url", "image_0"]] = df[
    ["p_id", "v_id", "v_image_url", "image_0"]
].fillna("")
df.loc[:, df.select_dtypes(object).columns.tolist()] = df.select_dtypes(object).fillna(
    ""
)
df.loc[:, df.select_dtypes(int).columns.tolist()] = df.select_dtypes(int).fillna(0)
df.loc[:, df.select_dtypes(float).columns.tolist()] = df.select_dtypes(float).fillna(0)
df.loc[:, ["p_id", "v_id", "v_image_url", "image_0"]] = df[
    ["p_id", "v_id", "v_image_url", "image_0"]
].replace("", nan)

b = get_all_brand_ids()
c = get_all_category_ids()

# awesome
for brand in df[~df.BRAND.isin(list(b.values()))].BRAND.unique():
    b.update({create_brand(brand): brand})
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
    for i in range(int(str(year - 3)) + int(month >= 5), int(year) + int(month >= 11))
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

df["listOnAmazon"] = ~df.BRAND.isin(amazon_excluded_vendors)

df.to_pickle(f"{DATA_DIR}/ready.pkl")

gb = df.groupby("webName")

new = gb.filter(lambda g: g.p_id.count() == 0).groupby("webName", sort=False)
old = gb.filter(
    lambda g: (g.lModified.max() > (dt.datetime.now() - dt.timedelta(days=daysAgo)))
    & (g.p_id.count() == 1)
).groupby("webName", sort=False)

product_payloads_for_update = []
for name, g in old:
    try:
        product_payloads_for_update.append(product_update_payload(g))
    except Exception:
        print("Couldn't create update payload for", name)
        continue

product_payloads_for_creation = []
for name, g in new:
    try:
        product_payloads_for_creation.append(product_creation_payload(g))
    except Exception:
        print("Couldn't create creation payload for", name)
        continue

# %% UPDATE

updated = []
failed_to_update = []
if len(product_payloads_for_update) > 0:
    print(f"Updating {len(product_payloads_for_update)} products in BigCommerce...")
    sleep(1)
    for i, u in tqdm(enumerate(product_payloads_for_update)):
        uid = u.pop("id")

        res = update_product(uid, u)
        update_custom_field(uid, "eBay Sale Price", u["amazon_price"])
        if u["list_on_amazon"]:
            update_custom_field(uid, "Amazon Status", "Enabled")
        else:
            update_custom_field(uid, "Amazon Status", "Disabled")

        if all([r.ok for r in res]):
            updated.append(res)
        elif any([r.status_code == 429 for r in res]):
            sleep(30)
            res = update_product(uid, u, slow=True)
            update_custom_field(uid, "eBay Sale Price", u["amazon_price"])
            if u["list_on_amazon"]:
                update_custom_field(uid, "Amazon Status", "Enabled")
            else:
                update_custom_field(uid, "Amazon Status", "Disabled")
            if all([r.ok for r in res]):
                updated.append(res)

        else:
            failed_to_update.append(res)

# %% CREATE

created = []
failed_to_create = []
if len(product_payloads_for_creation) > 0:
    print(f"Creating {len(product_payloads_for_creation)} products in BigCommerce...")
    sleep(1)

for i, c in tqdm(enumerate(product_payloads_for_creation)):
    res = create_product(c)
    if not res.ok:
        if res.reason == "Too Many Requests" or res.status_code == 429:
            try:
                sleep(int(res.headers["X-Rate-Limit-Time-Reset-Ms"]) / 1000)
            except KeyError:
                sleep(int(res.headers["X-Rate-Limit-Time-Reset-Ms".lower()]) / 1000)
                res = retry_request_using_response(res)
        if res.reason == "Conflict":
            if "product sku is a duplicate" in res.text:
                conflict_sku = c["sku"]
                conflict_products = get_product_by_sku(conflict_sku).json()["data"]
                for cp in conflict_products:
                    delete_product(cp["id"])
                res = retry_request_using_response(res)
            if "product name is a duplicate" in res.text:
                conflict_name = c["name"]
                conflict_products = get_product_by_name(conflict_name).json()["data"]
                for cp in conflict_products:
                    delete_product(cp["id"])
                res = retry_request_using_response(res)
        if (
            "could not be processed and may not be valid image" in res.text
            or "could not be downloaded and may be invalid"
        ):
            broken_image_urls = []
            if "images" in c:
                ims = c.pop("images")
                for im in ims:
                    if "image_url" in im:
                        broken_image_urls.append(im["image_url"])
            if "variants" in c:
                for v in c["variants"]:
                    if "image_url" in v:
                        im = v.pop("image_url")
                        broken_image_urls.append(im)
            bad_image_skus = list(
                set(
                    [
                        re.search(r"(\d-\d{5,6}_?\d?)", url).group(1).split("_")[0]
                        for url in broken_image_urls
                        if re.search(r"\d-\d{5,6}_?\d?", url)
                    ]
                )
            )
            mdf.loc[bad_image_skus, mdf.columns != "description"] = nan
            mdf.to_pickle(f"{DATA_DIR}/media.pkl")
            c["is_visible"] = False
            res = create_product(c)
    # res had been written over many times potentially,
    # which is why this is not an `elif` paired with the `if` above
    if res.ok:
        created.append(res)
        j = res.json()["data"]
        p_id = str(j["id"])
        # add custom fields
        update_custom_field(p_id, "eBay Sale Price", c["amazon_price"])
        if c["list_on_amazon"]:
            update_custom_field(p_id, "Amazon Status", "Enabled")
        else:
            update_custom_field(p_id, "Amazon Status", "Disabled")
        cat = str(j["categories"][0])
        sale_price = str(j["sale_price"])
        if cat in to_ebay_map:
            update_custom_field(p_id, "eBay Category ID", cat)
        else:
            update_custom_field(p_id, "eBay Category ID", "0")

    else:
        failed_to_create.append(res)


with open(f"{LOGS_DIR}/failed_to_create.log", "w") as ftc_log_file:
    for creation_failure_response in failed_to_create:
        original_payload = json.loads(creation_failure_response.request.body)
        response = creation_failure_response.json()

        ftc_log_file.write(json.dumps(response["errors"]) + "\n")
        ftc_log_file.write(
            f"name: {original_payload['name']}, sku: {original_payload['sku']}\n\n"
        )

send_to_quivers()

print("Runtime:", dt.datetime.now() - a)

debug = True
