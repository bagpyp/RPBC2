import requests

from config import base, headers


def get_big_commerce_orders(status_id, i):
    url = base + f"v2/orders?status_id={status_id}" + f"&limit=50&page={i}"
    res = requests.get(url, headers=headers)
    return res
