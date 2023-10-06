import datetime as dt
import json
from json import JSONDecodeError

import requests

from secret_info import base, headers, sls_base, sls_headers


def _get_orders(status_id, i):
    url = base + f"v2/orders?status_id={status_id}" + f"&limit=50&page={i}"
    res = requests.get(url, headers=headers)
    return res


def new_orders(kind="orders"):
    print(f"pulling new {kind} from BigCommerce...")
    status_ids = []
    if kind == "orders":
        status_ids = [2, 7, 9, 10, 11, 12]
    elif kind == "returns":
        status_ids = [4, 5]

    orders = []
    for status_id in status_ids:
        n = 1
        while _get_orders(status_id, i=n).text:
            nth_orders = _get_orders(status_id, i=n).json()
            orders.extend(nth_orders)
            n += 1
    orders = sorted(orders, key=lambda k: int(k["id"]))

    with open(f"data/bc_{kind}.json") as file:
        # SOME OF THESE MIGHT NOW BE RETURNS, AND NOT IN `orders`
        try:
            archive = json.load(file)
        except JSONDecodeError:
            with open(f"data/bc_{kind}.json", "w") as file:
                json.dump(orders, file)
            archive = orders
    archived_ids = [o["id"] for o in archive]
    # distinguish what's not in archive and store new orders
    new_orders = [o for o in orders if o["id"] not in archived_ids]
    # either there are some orders, or not!
    if new_orders:
        with open(f"data/bc_{kind}.json", "w") as file:
            # HERE WE NEED A UNION OF BOTH 'orders' AND 'archive'
            # NOT JUST `orders`
            json.dump(archive + new_orders, file)
    for o in new_orders:
        o["products"] = requests.get(o["products"]["url"], headers=headers).json()
    orders = []
    for no in new_orders:
        order = {"id": str(no["id"])}
        # ADD CHANNELS
        external_source = str(no["external_source"]).lower()
        if "walmart" in external_source:
            order["payment_id"] = no["staff_notes"].split("\t")[1].split("\n")[0]
            order["channel"] = "WALMART"
            order["payment_zone"] = "PayPal"
        elif "google" in external_source:
            order["payment_id"] = str(no["external_id"])
            order["channel"] = "GOOGLE"
            # TODO change after payments set up in google if necessary
            order["payment_zone"] = "PayPal"
        elif "facebook" in external_source:
            order["payment_id"] = str(no["external_id"])
            order["channel"] = "FACEBOOK"
            order["payment_zone"] = "FacebookMarketplace"
        elif "ebay" in external_source:
            order["payment_id"] = str(no["ebay_order_id"])
            order["channel"] = "EBAY"
            order["payment_zone"] = "Ebay"
        elif "amazon" in external_source:
            order["payment_id"] = ""
            order["channel"] = "AMAZON"
            order["payment_zone"] = "Amazon"
        else:
            order["payment_id"] = no["payment_provider_id"]
            order["channel"] = "BIGCOMMERCE"
            if "authorize.net" in no["payment_method"].lower():
                order["payment_zone"] = "Authorize.Net"
            elif no["payment_method"].lower() == "paypal":
                order["payment_zone"] = "PayPal"
            else:
                order["payment_zone"] = "BigCommerce"

        # TODO decide tz info
        order["created_date"] = dt.datetime.strptime(
            " ".join(no["date_created"].split(" ")[:-1]), "%a, %d %b %Y %H:%M:%S"
        ).strftime("%Y-%m-%dT%H:%M:%S")
        order["num_items"] = len(no["products"])
        order["total_amt"] = round(float(no["total_ex_tax"]), 2)
        order["status"] = no["status"]
        products = []

        for p in no["products"]:
            product = {
                "sku": p["sku"],
                "qty": int(p["quantity"]),
                "amt_per": round(float(p["price_ex_tax"]), 2),
                "amt_total": round(float(p["total_ex_tax"]), 2),
            }
            products.append(product)
        order["products"] = products

        orders.append(order)
    return orders


def new_sls_orders(kind="orders"):
    i = 1
    url = sls_base + "orders"
    res = requests.get(url, headers=sls_headers).json()
    sls_orders = res["data"]
    while res["meta"]["has_next"]:
        i += 1
        res = requests.get(url + f"?page={i}", headers=sls_headers)
        res = res.json()
        sls_orders.extend(res["data"])

    orders = sorted(sls_orders, key=lambda k: k["created_at"])

    with open(f"data/sls_{kind}.json") as file:
        archive = json.load(file)
    archived_ids = [o["order_id"] for o in archive]
    new_orders = [o for o in orders if o["order_id"] not in archived_ids]
    if new_orders:
        with open(f"data/sls_{kind}.json", "w") as file:
            json.dump(archive + new_orders, file)
    # return new_orders
    orders = []
    for no in new_orders:
        order = {}
        # VARIABLE -
        order["id"] = str(no["order_id"])
        order["payment_id"] = "external"
        order["channel"] = "SIDELINE"  # associate
        order["payment_zone"] = "SidelineSwap"  # customer.first_name
        # VARIABLE ^
        order["created_date"] = no["created_at"].split(".")[0]
        order["num_items"] = 1
        order["total_amt"] = round(float(no["you_earned"]), 2)
        order["products"] = [
            {
                "sku": no["item_sku"],
                "qty": 1,
                "amt_per": no["you_earned"],
                "amt_total": no["you_earned"],
            }
        ]
        if "shipment" in no:
            if "status" in no["shipment"]:
                order["status"] = no["shipment"]["status"]
            else:
                order["status"] = "NO STATUS"
        else:
            order["status"] = "NO STATUS"
        orders.append(order)

    statuses = []
    if kind == "orders":
        statuses = ["Pending_shipment", "Shipped", "Delivered"]
    elif kind == "returns":
        statuses = ["Cancelled"]
    return [o for o in orders if o["status"].lower() in [s.lower() for s in statuses]]


def get_all_orders():
    return sorted(new_sls_orders() + new_orders(), key=lambda k: k["created_date"])


def get_all_returns():
    return sorted(
        new_sls_orders(kind="returns") + new_orders(kind="returns"),
        key=lambda k: k["created_date"],
    )
