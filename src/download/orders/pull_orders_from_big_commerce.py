import datetime as dt
import json
from json import JSONDecodeError

import requests

from config import headers
from src.api.orders import get_bc_orders
from src.util import DATA_DIR


def pull_orders_from_big_commerce(kind="orders"):
    print(f"Pulling new {kind} from BigCommerce...")
    all_orders = get_bc_orders(kind=kind)

    with open(f"{DATA_DIR}/bc_{kind}.json") as bc_order_file:
        # SOME OF THESE MIGHT NOW BE RETURNS, AND NOT IN `archive`
        try:
            archive = json.load(bc_order_file)
        except JSONDecodeError:
            with open(f"{DATA_DIR}/bc_{kind}.json", "w") as bc_order_file_overwrite:
                # if the _orders file is corrupted, this will place all orders
                # in the archive, ensuring that 10k receipts won't be written
                json.dump(all_orders, bc_order_file_overwrite)
            archive = all_orders
    archived_ids = [o["id"] for o in archive]
    new_orders = [o for o in all_orders if o["id"] not in archived_ids]

    orders = []
    if new_orders:
        # add those new orders to the archive
        with open(f"{DATA_DIR}/bc_{kind}.json", "w") as file:
            json.dump(archive + new_orders, file)
        # populate list with order objects
        for new_order in new_orders:
            order = _build_order_from_response(new_order)
            orders.append(order)
    return orders


def _build_order_from_response(new_order):
    order = {"id": str(new_order["id"])}
    # ADD CHANNELS
    external_source = str(new_order["external_source"]).lower()
    if "walmart" in external_source:
        order["payment_id"] = (
            new_order["staff_new_ordertes"].split("\t")[1].split("\n")[0]
        )
        order["channel"] = "WALMART"
        order["payment_zone"] = "PayPal"
    elif "google" in external_source:
        order["payment_id"] = str(new_order["external_id"])
        order["channel"] = "GOOGLE"
        # TODO change after payments set up in google if necessary
        order["payment_zone"] = "PayPal"
    elif "facebook" in external_source:
        order["payment_id"] = str(new_order["external_id"])
        order["channel"] = "FACEBOOK"
        order["payment_zone"] = "FacebookMarketplace"
    elif "ebay" in external_source:
        order["payment_id"] = str(new_order["ebay_order_id"])
        order["channel"] = "EBAY"
        order["payment_zone"] = "Ebay"
    elif "amazon" in external_source:
        order["payment_id"] = ""
        order["channel"] = "AMAZON"
        order["payment_zone"] = "Amazon"
    else:
        order["payment_id"] = new_order["payment_provider_id"]
        order["channel"] = "BIGCOMMERCE"
        if "authorize.net" in new_order["payment_method"].lower():
            order["payment_zone"] = "Authorize.Net"
        elif new_order["payment_method"].lower() == "paypal":
            order["payment_zone"] = "PayPal"
        else:
            order["payment_zone"] = "BigCommerce"

    order["created_date"] = dt.datetime.strptime(
        " ".join(new_order["date_created"].split(" ")[:-1]), "%a, %d %b %Y %H:%M:%S"
    ).strftime("%Y-%m-%dT%H:%M:%S")
    order["total_amt"] = round(float(new_order["total_ex_tax"]), 2)
    order["status"] = new_order["status"]

    new_order["products"] = requests.get(
        new_order["products"]["url"], headers=headers
    ).json()
    order["num_items"] = len(new_order["products"])
    products = []
    for p in new_order["products"]:
        product = {
            "sku": p["sku"],
            "qty": int(p["quantity"]),
            "amt_per": round(float(p["price_ex_tax"]), 2),
            "amt_total": round(float(p["total_ex_tax"]), 2),
        }
        products.append(product)
    order["products"] = products

    return order
