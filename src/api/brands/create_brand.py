import requests

from config import base, headers


def create_brand(name):
    url = base + "v3/catalog/brands"
    h = headers.copy()
    h.update({"content-type": "application/json", "accept": "application/json"})
    d = {"name": f"{name}"}
    return requests.post(url, headers=h, json=d)
