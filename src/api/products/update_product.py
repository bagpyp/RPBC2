import time

import requests

from config import headers, base


def update_product(id_, data):
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
            time.sleep(0.01)
            variant_url = url + f"/variants/{variant_data.pop('id')}"
            res = requests.put(variant_url, headers=h, json=variant_data)
            # don't return variant not found res in res array
            # TODO: why tf not?
            if res.status_code != 404:
                responses.append(res)
    return responses
