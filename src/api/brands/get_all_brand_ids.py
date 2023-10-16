import requests

from config import base, headers
from src.util import call_iteratively


def _get_brand_ids(i=1):
    url = base + "v3/catalog/brands" + f"?limit=50&page={i}"
    res = requests.get(url, headers=headers)
    return res


def get_all_brand_ids():
    data = call_iteratively(_get_brand_ids)
    return {d["id"]: d["name"] for d in data}
