import requests

from config import headers, base


def get_product_id_by_name(name_):
    h = headers.copy()
    url = base + f"v3/catalog/products?name={name_}&include_fields=id"
    res = requests.get(url, headers=h)
    return res
