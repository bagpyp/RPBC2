import requests

from config import sls_base, sls_headers


def get_sls_orders():
    i = 1
    url = sls_base + "orders"
    res = requests.get(url, headers=sls_headers).json()
    sls_orders = res["data"]
    while res["meta"]["has_next"]:
        i += 1
        res = requests.get(url + f"?page={i}", headers=sls_headers)
        res = res.json()
        sls_orders.extend(res["data"])
    return sls_orders
