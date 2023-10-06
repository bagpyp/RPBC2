import requests

from secret_info import headers, base


def _create_custom_field(product_id, key, value):
    url = base + f"v3/catalog/products/{product_id}/custom-fields"
    data = {
        "name": key,
        "value": str(value),
    }
    h = headers.copy()
    h.update({"content-type": "application/json"})
    res = requests.post(url, headers=h, json=data)
    return res


def _get_custom_field_id(product_id, key):
    url = base + f"v3/catalog/products/{product_id}/custom-fields"
    h = headers.copy()
    res = requests.get(url, headers=h)
    fields = res.json()["data"]
    for d in fields:
        if d["name"] == key:
            return d["id"]


def update_custom_field(product_id, key, value):
    custom_field_id = _get_custom_field_id(product_id, key)
    if custom_field_id:
        url = base + f"v3/catalog/products/{product_id}/custom-fields/{custom_field_id}"
        data = {
            "name": key,
            "value": str(value),
        }
        h = headers.copy()
        h.update({"accept": "application/json", "content-type": "application/json"})
        res = requests.put(url, headers=h, json=data)
        return res
    else:
        return _create_custom_field(product_id, key, value)
