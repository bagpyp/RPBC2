import requests

from config import headers, base


def get_product_by_sku(sku):
    h = headers.copy()
    url = base + f"v3/catalog/products?sku={sku}"
    res = requests.get(url, headers=h)
    return res


def get_product_by_name(name_):
    h = headers.copy()
    url = base + f"v3/catalog/products?name={name_}"
    res = requests.get(url, headers=h)
    return res


def _get_products(i=1):
    url = (
        base
        + "v3/catalog/products"
        + f"?limit=10&page={i}"
        + "&include=variants,images"
    )
    res = requests.get(url, headers=headers)
    return res
