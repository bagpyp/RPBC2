import requests

from config import base, headers


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
