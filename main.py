# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:29:51 2020

@author: Bagpyp
"""
import datetime as dt

import pandas as pd
from numpy import nan

from config import days_to_update, run_offline
from scripts.quivers import send_to_quivers
from src.api import delete_product
from src.download.orders import (
    process_orders_and_returns,
)
from src.download.products import (
    get_all_product_data_from_big_commerce,
    download_brand_ids,
    download_category_ids,
)
from src.product_images import (
    build_image_locations_from_file_structure,
    persist_web_media,
)
from src.server import read_ecm_data_into_dataframe
from src.transformations import (
    attach_web_data_to_products,
    build_payloads,
    build_product_group_structure,
    clean_and_filter,
    collect_images_from_product_children,
    prepare_df_for_upload,
)
from src.upload.create import create_products
from src.upload.update import update_products
from src.util.path_utils import DATA_DIR

a = dt.datetime.now()
print(
    f"Began {a}, processing changes in RetailPro over the last {days_to_update} days..."
)

if run_offline:
    df = pd.read_pickle(f"{DATA_DIR}/fromECM.pkl")
    pdf = pd.read_pickle(f"{DATA_DIR}/products.pkl")

else:
    process_orders_and_returns()
    df = read_ecm_data_into_dataframe()
    pdf = get_all_product_data_from_big_commerce
    download_brand_ids()
    download_category_ids()

df = clean_and_filter(df)
df = build_product_group_structure(df)
df = attach_web_data_to_products(df, pdf)
df = collect_images_from_product_children(df)

if not run_offline:
    persist_web_media(df)

"""some hood shit"""
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
""" end of hood shit """

df.update(pd.read_pickle(f"{DATA_DIR}/media.pkl"))

if run_offline:
    fileDf = pd.read_pickle(f"{DATA_DIR}/fileDf.pkl")
else:
    fileDf = build_image_locations_from_file_structure()

df = df.join(fileDf)
df = prepare_df_for_upload(df)
product_payloads_for_update, product_payloads_for_creation = build_payloads(df)

if not run_offline:
    update_products(product_payloads_for_update)
    create_products(product_payloads_for_creation)
    send_to_quivers()
