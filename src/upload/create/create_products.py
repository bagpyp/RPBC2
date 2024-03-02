import datetime as dt
import json
import os
import re
from glob import glob
from time import sleep

from tqdm import tqdm

from src.api.products import (
    create_product,
    get_product_id_by_sku,
    delete_product,
    get_product_id_by_name,
    update_custom_field,
)
from src.constants import bc_category_id_to_ebay_category_id
from src.util import LOGS_DIR, IMAGES_DIR


def create_products(payloads):
    if len(payloads) > 0:
        print(f"Creating {len(payloads)} products in BigCommerce...")

    all_bad_image_skus = []
    failed_to_create = []

    def recursive_create(c):
        res = create_product(c)
        if res.ok:
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
            # eBay Status
            list_on_ebay = c["list_on_ebay"]
            update_custom_field(
                p_id, "eBay Status", "Enabled" if list_on_ebay else "Disabled"
            )
            # WalMart Status
            list_on_walmart = c["list_on_walmart"]
            update_custom_field(
                p_id, "WalMart Status", "Enabled" if list_on_walmart else "Disabled"
            )
            # eBay Category
            bc_category = str(json_response_payload["categories"][0])
            update_custom_field(
                p_id,
                "eBay Category ID",
                bc_category_id_to_ebay_category_id.get(bc_category, "0"),
            )
            return
        else:
            if res.reason == "Too Many Requests" or res.status_code == 429:
                try:
                    sleep(int(res.headers["X-Rate-Limit-Time-Reset-Ms"]) / 1000)
                except KeyError:
                    sleep(int(res.headers["X-Rate-Limit-Time-Reset-Ms".lower()]) / 1000)
                recursive_create(c)

            elif res.reason == "Conflict" and "product sku is a duplicate" in res.text:
                conflict_sku = c["sku"]
                conflict_products = get_product_id_by_sku(conflict_sku)
                if conflict_products:
                    for cp in conflict_products:
                        delete_product(cp)
                    recursive_create(c)
                else:
                    failed_to_create.append(res)
                    return
            elif res.reason == "Conflict" and "product name is a duplicate" in res.text:
                conflict_name = c["name"]
                conflict_products = get_product_id_by_name(conflict_name)
                if conflict_products:
                    for cp in conflict_products:
                        delete_product(cp)
                    recursive_create(c)
                else:
                    failed_to_create.append(res)
                    return
            elif ("could not be processed and may not be valid image" in res.text) or (
                "could not be downloaded and may be invalid" in res.text
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
                c["is_visible"] = False
                recursive_create(c)
            else:
                failed_to_create.append(res)
                return

    for i, create_payload in tqdm(enumerate(payloads)):
        recursive_create(create_payload)

    # remove corrupt images from images/ folder
    for bis in all_bad_image_skus:
        if bis[:2] in ["0-", "2-"]:
            for file_path in glob(f"{IMAGES_DIR}/base/{bis}_*"):
                if os.path.exists(file_path):
                    os.rename(file_path, file_path.replace("/base/", "/removed/"))
        elif bis[:2] == "1-":
            for file_path in glob(f"{IMAGES_DIR}/variant/{bis}.jpeg"):
                if os.path.exists(file_path):
                    os.rename(file_path, file_path.replace("/base/", "/removed/"))

    if failed_to_create:
        with open(f"{LOGS_DIR}/failed_to_create.log", "w") as ftc_log_file:
            ftc_log_file.write(str(dt.datetime.now()) + "\n\n")
            for creation_failure_response in failed_to_create:
                original_payload = json.loads(creation_failure_response.request.body)
                response = creation_failure_response.json()

                ftc_log_file.write(json.dumps(response["errors"]) + "\n")
                ftc_log_file.write(
                    f"name: {original_payload['name']}, sku: {original_payload['sku']}\n\n"
                )
