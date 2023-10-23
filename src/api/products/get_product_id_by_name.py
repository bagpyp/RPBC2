import requests

from config import headers, base


def get_product_id_by_name(name_):
    h = headers.copy()
    url = base + rf"v3/catalog/products?name={name_}&include_fields=id"
    res = requests.get(url, headers=h)
    data = res.json().get("data", [])
    if data:
        return [d["id"] for d in data]
    else:
        url = base + rf"v3/catalog/products?keyword={name_}&include_fields=id"
        res = requests.get(url, headers=h)
        data = res.json().get("data", [])
    return [d["id"] for d in data]


if __name__ == "__main__":
    conflict_name = "Qst Spark + M10 Gw 22-23"
    products = get_product_id_by_name(conflict_name)
    print(products)
