from pprint import pprint

import pandas as pd
import requests

from config import headers, base
from src.util import DATA_DIR

bad_skus = [
    "1-108103",
    "1-118588",
    "1-211397",
    "1-211348",
    "1-211342",
    "1-219377",
    "1-29680",
    "1-206587",
    "1-119488",
]


def check_bad_skus(skus):
    ready = pd.read_pickle(f"{DATA_DIR}/ready.pkl")
    products = pd.read_pickle(f"{DATA_DIR}/products.pkl")
    quants = {}
    for sku in skus:
        pid, vid = products.loc[products.v_sku == sku, ["p_id", "v_id"]].values[0]
        bc_qty = get_qty_by_pid_vid(pid, vid)
        rp_qty = ready.loc[ready.sku == sku, "qty"].iat[0]
        quants[sku] = {"bc": bc_qty, "rp": rp_qty}
    pprint(quants)


def get_qty_by_pid_vid(pid, vid):
    url = f"{base}v3/catalog/products/{pid}/variants/{vid}"
    res = requests.get(url, headers=headers.copy())
    data = res.json()["data"]
    return data["inventory_level"]


if __name__ == "__main__":
    check_bad_skus(bad_skus)
