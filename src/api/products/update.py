import time
from time import sleep

import requests
from tqdm import tqdm

from config import headers, base
from src.api import update_custom_field
from src.util.path_utils import LOGS_DIR


def update_product(id_, data, slow=False):
    responses = []
    url = base + f"v3/catalog/products/{id_}"
    h = headers.copy()
    h.update({"content-type": "application/json"})
    if "variants" not in data:
        res = requests.put(url, headers=h, json=data)
        responses.append(res)
    else:
        variants = data.pop("variants")
        res = requests.put(url, headers=h, json=data)
        responses.append(res)
        for variant_data in variants:
            variant_url = url + f"/variants/{variant_data.pop('id')}"
            res = requests.put(variant_url, headers=h, json=variant_data)
            if slow:
                time.sleep(1)
            else:
                time.sleep(0.1)
            # don't return variant not found res in res array
            # TODO: why tf not?
            if res.status_code != 404:
                responses.append(res)
    return responses


def product_update_payload(g):
    product = {}
    g = g.fillna("").to_dict("records")
    r = g[0]
    product.update(
        {
            "id": r["p_id"],
            "inventory_level": r["qty"],
            "sale_price": r["pSale"],
            "price": r["pMAP"],
            "list_on_amazon": r["listOnAmazon"],
            "amazon_price": r["pAmazon"],
            "retail_price": r["pMSRP"],
        }
    )
    if r["clearance_cat"] != "":
        product.update({"categories": [int(r["cat"]), int(r["clearance_cat"])]})
    else:
        product.update({"categories": [int(r["cat"])]})
    if r["image_0"] != "":
        product.update({"is_visible": True})
    elif r["image_0"] == "":
        product.update({"is_visible": False})
    if len(g) > 1:
        variants = []
        for h in g[1:]:
            variant = {}
            variant.update(
                {
                    "id": h["v_id"],
                    "inventory_level": h["qty"],
                    "price": h["pMAP"],
                    "amazon_price": h["pAmazon"],
                    "sale_price": h["pSale"],
                    "retail_price": h["pMSRP"],
                }
            )
            variants.append(variant)
        product.update({"variants": variants})
    return product


def update_products(payloads):
    updated = []
    failed_to_update = []
    if len(payloads) > 0:
        print(f"Updating {len(payloads)} products in BigCommerce...")
        sleep(1)
        for i, u in tqdm(enumerate(payloads)):
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

    if failed_to_update:
        with open(f"{LOGS_DIR}/failed_to_update.log", "w") as ftu_log_file:
            for update_failure_response_group in failed_to_update:
                for update_failure_response in update_failure_response_group:
                    ftu_log_file.write(update_failure_response.text + "\n")
