import json
import re
from time import sleep

import pandas as pd
from numpy import nan
from tqdm import tqdm

from src.api import (
    create_product,
    retry_request_using_response,
    get_product_by_sku,
    delete_product,
    get_product_by_name,
    update_custom_field,
)
from src.constants import to_ebay_map
from src.util.path_utils import DATA_DIR, LOGS_DIR


def create_products(payloads):
    created = []
    failed_to_create = []

    mdf = pd.read_pickle(f"{DATA_DIR}/media.pkl")

    if len(payloads) > 0:
        print(f"Creating {len(payloads)} products in BigCommerce...")
        sleep(1)

    for i, c in tqdm(enumerate(payloads)):
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
                    conflict_products = get_product_by_name(conflict_name).json()[
                        "data"
                    ]
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

    if failed_to_create:
        with open(f"{LOGS_DIR}/failed_to_create.log", "w") as ftc_log_file:
            for creation_failure_response in failed_to_create:
                original_payload = json.loads(creation_failure_response.request.body)
                response = creation_failure_response.json()

                ftc_log_file.write(json.dumps(response["errors"]) + "\n")
                ftc_log_file.write(
                    f"name: {original_payload['name']}, sku: {original_payload['sku']}\n\n"
                )
