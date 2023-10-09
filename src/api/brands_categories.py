import requests

from config import headers, base
from src.api.request_utils import call_iteratively


def _get_brands(i=1):
    url = base + "v3/catalog/brands" + f"?limit=50&page={i}"
    res = requests.get(url, headers=headers)
    return res


def get_all_brand_ids():
    data = call_iteratively(_get_brands)
    return {d["id"]: d["name"] for d in data}


def create_brand(name):
    url = base + "v3/catalog/brands"
    h = headers.copy()
    h.update({"content-type": "application/json", "accept": "application/json"})
    d = {"name": f"{name}"}
    res = requests.post(url, headers=h, json=d)
    if res.ok:
        return res.json()["data"]["id"]


def get_all_category_ids():
    url = base + "v3/catalog/categories/tree"
    res = requests.get(url, headers=headers)
    cat = {}
    for i in res.json()["data"]:
        cat.update({i["id"]: i["name"]})
        for j in i["children"]:
            cat.update({j["id"]: i["name"] + "/" + j["name"]})
            for k in j["children"]:
                cat.update({k["id"]: i["name"] + "/" + j["name"] + "/" + k["name"]})
    return cat
