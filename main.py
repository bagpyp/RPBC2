# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:29:51 2020

@author: Bagpyp
"""
import datetime as dt

import pandas as pd

from config import days_to_update, run_offline
from scripts.quivers import send_to_quivers
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
    delete_conflict_products,
)
from src.upload.create import create_products
from src.upload.update import update_products
from src.util.path_utils import DATA_DIR

start_time = dt.datetime.now()
print(
    f"Began {start_time}, processing changes in RetailPro over the last {days_to_update} days..."
)

if run_offline:
    df = pd.read_pickle(f"{DATA_DIR}/fromECM.pkl")
    pdf = pd.read_pickle(f"{DATA_DIR}/products.pkl")

else:
    process_orders_and_returns()
    df = read_ecm_data_into_dataframe()
    pdf = get_all_product_data_from_big_commerce()
    download_brand_ids()
    download_category_ids()

df = clean_and_filter(df)
df = build_product_group_structure(df)
pdf = delete_conflict_products(df, pdf)
df = attach_web_data_to_products(df, pdf)
df = collect_images_from_product_children(df)

if not run_offline:
    persist_web_media(df)

df = df.set_index("sku")
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
