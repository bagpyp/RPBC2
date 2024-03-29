import requests

from config import headers, base


def update_product(product_id, data):
    responses = []
    url = base + f"v3/catalog/products/{product_id}"
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
            variant_id = variant_data.pop("id")
            variant_url = (
                base
                + f"v3/catalog/products/{product_id}/variants/{variant_id}"
            )
            res = requests.put(variant_url, headers=h, json=variant_data)
            responses.append(res)
    return responses
