# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:29:51 2020

@author: Bagpyp
"""
import datetime as dt

import pandas as pd

from config import update_window_hours, apply_changes
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


def main():
    start_time = dt.datetime.now()
    print(
        f"Began at {start_time}, processing changes in RetailPro over the last {update_window_hours} hours..."
    )

    if not apply_changes:
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

    if apply_changes:
        persist_web_media(df)

    df = df.set_index("sku")
    df.update(pd.read_pickle(f"{DATA_DIR}/media.pkl"))

    if apply_changes:
        file_structure_df = build_image_locations_from_file_structure()
    else:
        file_structure_df = pd.read_pickle(f"{DATA_DIR}/fileDf.pkl")

    df = df.join(file_structure_df)
    df = prepare_df_for_upload(df)

    product_payloads_for_update, product_payloads_for_creation = build_payloads(df)

    if apply_changes:
        update_products(product_payloads_for_update)
        create_products(product_payloads_for_creation)
        send_to_quivers()

    end_time = dt.datetime.now()
    print(f"Finished at {end_time}, duration process was {end_time - start_time}")


if __name__ == "__main__":
    main()
