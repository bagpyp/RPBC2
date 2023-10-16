import json
import os
import re
from glob import glob
from time import sleep

import pandas as pd
from numpy import nan
from tqdm import tqdm

from src.api.products import (
    create_product,
    get_product_id_by_sku,
    delete_product,
    get_product_id_by_name,
    update_custom_field,
)
from src.constants import to_ebay_map
from src.util import DATA_DIR, LOGS_DIR, IMAGES_DIR


def create_products(payloads):
    if len(payloads) > 0:
        print(f"Creating {len(payloads)} products in BigCommerce...")
        sleep(1)

    mdf_changed = False
    mdf = pd.read_pickle(f"{DATA_DIR}/media.pkl")

    all_bad_image_skus = []

    created = []
    failed_to_create = []
    for i, c in tqdm(enumerate(payloads)):
        res = create_product(c)
        if not res.ok:
            if res.reason == "Too Many Requests" or res.status_code == 429:
                try:
                    sleep(int(res.headers["X-Rate-Limit-Time-Reset-Ms"]) / 1000)
                except KeyError:
                    sleep(int(res.headers["X-Rate-Limit-Time-Reset-Ms".lower()]) / 1000)
                res = create_product(c)
            if res.reason == "Conflict":
                if "product sku is a duplicate" in res.text:
                    conflict_sku = c["sku"]
                    conflict_products = get_product_id_by_sku(conflict_sku).json()[
                        "data"
                    ]
                    for cp in conflict_products:
                        delete_product(cp["id"])
                    res = create_product(c)
                if "product name is a duplicate" in res.text:
                    conflict_name = c["name"]
                    conflict_products = get_product_id_by_name(conflict_name).json()[
                        "data"
                    ]
                    for cp in conflict_products:
                        delete_product(cp["id"])
                    res = create_product(c)
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
                all_bad_image_skus.extend(bad_image_skus)
                mdf.loc[bad_image_skus, mdf.columns != "description"] = nan
                mdf_changed = True
                c["is_visible"] = False
                res = create_product(c)
        # res had been written over many times potentially,
        # which is why this is not an `elif` paired with the `if` above
        if res.ok:
            created.append(res)
            json_response_payload = res.json()["data"]
            p_id = str(json_response_payload["id"])

            # Amazon Price (called eBay price)
            amazon_price = c["amazon_price"]
            update_custom_field(p_id, "eBay Sale Price", amazon_price)
            # Amazon Status
            list_on_amazon = c["list_on_amazon"]
            update_custom_field(
                p_id, "Amazon Status", "Enabled" if list_on_amazon else "Disabled"
            )
            # eBay Category
            bc_category = str(json_response_payload["categories"][0])
            update_custom_field(
                p_id,
                "eBay Category ID",
                bc_category if bc_category in to_ebay_map else "0",
            )

        else:
            failed_to_create.append(res)

    # remove corrupt images from images/ folder
    for bis in all_bad_image_skus:
        if bis[:2] in ["0-", "2-"]:
            for file_path in glob(f"{IMAGES_DIR}/base/{bis}_*"):
                if os.path.exists(file_path):
                    os.remove(file_path)
        elif bis[:2] == "1-":
            for file_path in glob(f"{IMAGES_DIR}/variant/{bis}.jpeg"):
                if os.path.exists(file_path):
                    os.remove(file_path)

    # persist mdf changes in pickle
    if mdf_changed:
        mdf.to_pickle(f"{DATA_DIR}/media.pkl")

    if failed_to_create:
        with open(f"{LOGS_DIR}/failed_to_create.log", "w") as ftc_log_file:
            for creation_failure_response in failed_to_create:
                original_payload = json.loads(creation_failure_response.request.body)
                response = creation_failure_response.json()

                ftc_log_file.write(json.dumps(response["errors"]) + "\n")
                ftc_log_file.write(
                    f"name: {original_payload['name']}, sku: {original_payload['sku']}\n\n"
                )
