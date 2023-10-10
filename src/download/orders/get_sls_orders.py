import json

from src.api.orders.sideline_swap import get_sls_orders
from src.util.path_utils import DATA_DIR


def pull_orders_from_sideline_swap(kind="orders"):
    print(f"Pulling new {kind} from SidelineSwap...")
    sls_orders = get_sls_orders()

    orders = sorted(sls_orders, key=lambda k: k["created_at"])

    with open(f"{DATA_DIR}/sls_{kind}.json") as file:
        archive = json.load(file)
    archived_ids = [o["order_id"] for o in archive]
    new_orders = [o for o in orders if o["order_id"] not in archived_ids]
    if new_orders:
        with open(f"{DATA_DIR}/sls_{kind}.json", "w") as file:
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
