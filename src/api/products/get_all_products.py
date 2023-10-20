import requests

from config import headers, base
from src.util import call_iteratively


def _get_products(i=1):
    url = (
        base
        + "v3/catalog/products"
        + f"?limit=250&page={i}"
        + "&include=variants,images,custom_fields"
        + "&include_fields=id,name,sku,price,categories,brand_id,is_visible,"
        "date_created,date_modified,description"
    )
    res = requests.get(url, headers=headers)
    return res


def get_all_products():
    data = call_iteratively(_get_products)
    return data
