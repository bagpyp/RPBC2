import requests

from config import headers, base
from src.util import call_iteratively


def _get_products(i=1):
    url = (
        base
        + "v3/catalog/products"
        + f"?limit=10&page={i}"
        + "&include=variants,images"
    )
    res = requests.get(url, headers=headers)
    return res


def get_all_products():
    data = call_iteratively(_get_products)
    return data
