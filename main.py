# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:29:51 2020

@author: Bagpyp
"""
import datetime as dt

import pandas as pd
from numpy import nan

from config import days_to_update, run_offline, sync_sideline_swap
from scripts.quivers import send_to_quivers
from src.api import delete_product
from src.api.orders import get_all_orders, get_all_returns
from src.api.products.read import get_all_product_data_from_big_commerce
from src.product_images import build_image_locations_from_file_structure
from src.product_images import persist_web_media
from src.server import read_ecm_data_into_dataframe
from src.server import write_orders_to_ecm
from src.transformations import (
    attach_web_data_to_products,
    build_product_group_structure,
    clean_and_filter,
    collect_images_from_product_children,
    prepare_df_for_upload,
)
from src.upload.create import create_products, product_creation_payload
from src.upload.update import update_products, product_update_payload
from src.util.path_utils import DATA_DIR, INVOICES_DIR

a = dt.datetime.now()
print(
    f"Began {a}, processing changes in RetailPro over the last {days_to_update} days..."
)

# %% ORDERS AND RETURNS

if not run_offline:
    all_new_orders = get_all_orders(sync_sideline_swap)
    write_orders_to_ecm(all_new_orders)

    w = pd.read_csv(f"{INVOICES_DIR}/written.csv")
    all_new_returns = get_all_returns(sync_sideline_swap)
    write_orders_to_ecm(
        [
            ret
            for ret in all_new_returns
            if str(ret.get("id"))
            in w.comment1.apply(lambda x: x.split(" ")[1]).tolist()
        ],
        regular=False,
    )

# %% ECM

if run_offline:
    df = read_ecm_data_into_dataframe(bypass_ecm=True)
else:
    print("Pulling data from ECM on the server via PROC OUT")
    df = read_ecm_data_into_dataframe()

# %% TRANSFORM

df = clean_and_filter(df)

# %%  PRODUCT OPTIONS

df = build_product_group_structure(df)

# %%  JOIN AND MEDIATE

if run_offline:
    pdf = pd.read_pickle(f"{DATA_DIR}/products.pkl")
else:
    print("Pulling product data from BigCommerce")
    pdf = get_all_product_data_from_big_commerce()

df = attach_web_data_to_products(df, pdf)

# %% HANDLE IMAGES

df = collect_images_from_product_children(df)

if not run_offline:
    print("Archiving new images from BigCommerce")
    persist_web_media(df)


# %% DELETE CONFLICT PRODUCTS

nosync = df.groupby("webName").filter(
    lambda g: ((g.p_id.count() > 0) & (g[["p_id", "v_id"]].count().sum() < len(g)))
)

if not run_offline:
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


# %% ADD PRODUCT IMAGES AND DESCRIPTION TO DF

mdf = pd.read_pickle(f"{DATA_DIR}/media.pkl")
df.update(mdf)

if run_offline:
    df = pd.read_pickle(f"{DATA_DIR}/fileDf.pkl")
else:
    df = df.join(build_image_locations_from_file_structure())


# %% POST PROCESSING

# the below function issues an api call to get all category/brand ids
df = prepare_df_for_upload(df)

gb = df.groupby("webName")

new_products_gb = gb.filter(lambda g: g.p_id.count() == 0).groupby(
    "webName", sort=False
)
changed_products_gb = gb.filter(
    lambda g: (
        g.lModified.max() > (dt.datetime.now() - dt.timedelta(days=days_to_update))
    )
    & (g.p_id.count() == 1)
).groupby("webName", sort=False)

product_payloads_for_update = []
for name, g in changed_products_gb:
    try:
        product_payloads_for_update.append(product_update_payload(g))
    except Exception:
        print("Couldn't create update payload for", name)
        continue

product_payloads_for_creation = []
for name, g in new_products_gb:
    try:
        product_payloads_for_creation.append(product_creation_payload(g))
    except Exception:
        print("Couldn't create creation payload for", name)
        continue

# %% UPDATE AND CREATE

if not run_offline:
    update_products(product_payloads_for_update)
    create_products(product_payloads_for_creation)

# %% SEND RESULTS TO QUIVERS

if not run_offline:
    send_to_quivers()

print("Runtime:", dt.datetime.now() - a)

debug = True
