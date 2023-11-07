# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:29:51 2020

@author: Bagpyp
"""
import datetime as dt

import pandas as pd

from config import apply_changes, sync_sideline_swap
from scripts.quivers import send_to_quivers
from src.download.orders import get_all_orders, get_all_returns
from src.download.products import (
    pull_product_data_from_big_commerce,
    download_brand_ids,
    download_category_ids,
)
from src.product_images import (
    build_image_locations_from_file_structure,
    persist_web_media,
)
from src.server import (
    read_ecm_data_into_dataframe,
    write_orders_to_ecm,
    write_returns_to_ecm,
)
from src.transformations import (
    attach_web_data_to_products,
    build_product_group_structure,
    clean_and_filter,
    collect_images_from_product_children,
    prepare_df_for_upload,
    delete_conflict_products,
)
from src.upload.create import create_products, build_create_payloads
from src.upload.update import (
    update_products,
    build_update_payloads,
    batch_update_products,
)
from src.util import DATA_DIR, LOGS_DIR


def main():
    start_time = dt.datetime.now()
    print(f"Began at {start_time}, processing changes in RetailPro...")

    if not apply_changes:
        df = pd.read_pickle(f"{DATA_DIR}/fromECM.pkl")
        pdf = pd.read_pickle(f"{DATA_DIR}/products.pkl")

    else:
        all_new_orders = get_all_orders(sync_sideline_swap)
        write_orders_to_ecm(all_new_orders)

        all_new_returns = get_all_returns(sync_sideline_swap)
        write_returns_to_ecm(all_new_returns)

        df = read_ecm_data_into_dataframe()

        pdf = pull_product_data_from_big_commerce()
        download_brand_ids()
        download_category_ids()

    df = clean_and_filter(df)
    df = build_product_group_structure(df)
    pdf = delete_conflict_products(df, pdf)
    df = attach_web_data_to_products(df, pdf)
    df = collect_images_from_product_children(df)

    if apply_changes:
        persist_web_media(df)
        file_structure_df = build_image_locations_from_file_structure()
    else:
        file_structure_df = pd.read_pickle(f"{DATA_DIR}/fileDf.pkl")

    df = df.set_index("sku").join(file_structure_df)
    df = prepare_df_for_upload(df)

    product_payloads_for_update = build_update_payloads(df)
    product_payloads_for_creation = build_create_payloads(df)

    if apply_changes:
        update_products(product_payloads_for_update["product_groups"])
        batch_update_products(product_payloads_for_update["single_products"])
        create_products(product_payloads_for_creation)
        send_to_quivers()

    num_created = len(product_payloads_for_creation)
    num_updated = len(product_payloads_for_update["product_groups"]) + len(
        product_payloads_for_update["single_products"]
    )
    end_time = dt.datetime.now()
    print(f"Finished at {end_time}, duration process was {end_time - start_time}")

    with open(f"{LOGS_DIR}/runs.csv", "a") as run_file:
        run_file.write(
            f"{start_time},{end_time},{end_time - start_time},{num_updated},{num_created}\n"
        )


if __name__ == "__main__":
    main()
