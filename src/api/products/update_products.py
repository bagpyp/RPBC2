import requests

from config import headers, base


def update_products(data):
    url = base + f"v3/catalog/products?include_fields=id"
    h = headers.copy()
    h.update({"content-type": "application/json"})
    res = requests.put(url, headers=h, json=data)
    return res
