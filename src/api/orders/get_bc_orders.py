import requests

from config import base, headers


def _get_bc_orders_by_status_id(status_id, i):
    url = (
        base
        + f"v2/orders?status_id={status_id}"
        + f"&limit=50&page={i}"
        # + "&include_fields=id,external_source,external_id,external_id,ebay_order_id,payment_provider_id,"
        #   "payment_method,payment_method,date_created,total_ex_tax,status,products"
    )
    res = requests.get(url, headers=headers)
    return res


def get_bc_orders(kind="orders"):
    status_ids = []
    if kind == "orders":
        status_ids = [2, 7, 9, 10, 11, 12]
    elif kind == "returns":
        status_ids = [4, 5]

    orders = []
    for status_id in status_ids:
        n = 1
        while _get_bc_orders_by_status_id(status_id, i=n).text:
            nth_orders = _get_bc_orders_by_status_id(status_id, i=n).json()
            orders.extend(nth_orders)
            n += 1
    orders = sorted(orders, key=lambda k: int(k["id"]))
    return orders
