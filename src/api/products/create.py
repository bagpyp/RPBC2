import requests

from secret_info import headers, base


def create_product(data):
    url = base + "v3/catalog/products"
    h = headers.copy()
    h.update({"content-type": "application/json"})
    res = requests.post(url, headers=h, json=data)
    return res
