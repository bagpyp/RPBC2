import time

import requests

from config import headers, base


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
