import requests

from config import headers, base


def create_product(data):
    url = base + "v3/catalog/products?include_fields=id,categories"
    h = headers.copy()
    h.update({"content-type": "application/json"})
    res = requests.post(url, headers=h, json=data)
    return res
