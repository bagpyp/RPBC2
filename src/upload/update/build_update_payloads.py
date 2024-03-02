import datetime as dt

import pandas as pd

from config import overlap_seconds
from src.util import LOGS_DIR, DATA_DIR


def build_update_payloads(df):
    runs = pd.read_csv(f"{LOGS_DIR}/runs.csv")
    now = dt.datetime.now()
    last_start = runs.start.max()
    time_delta = now - pd.to_datetime(last_start)
    seconds_backward = time_delta.seconds + overlap_seconds  # ten minutes worth usually

    gb = df.groupby("webName")

    def sieve(g):
        """Returns True if product group g should be updated (as opposed to created or left alone)"""
        already_created_in_big_commerce = g.p_id.notna().sum() > 0
        was_updated_recently_in_retail_pro = g.lModified.max() > (
            dt.datetime.now() - dt.timedelta(seconds=seconds_backward)
        )
        quantities_unexpectedly_mismatched = (
            (g.qty != g.v_qty).any()
            if len(g) == 1
            else (g.loc[g.index[1] :, "qty"] != g.loc[g.index[1] :, "v_qty"]).any()
        )
        return already_created_in_big_commerce and (
            was_updated_recently_in_retail_pro or quantities_unexpectedly_mismatched
        )

    changed_products_gb = gb.filter(sieve).groupby("webName", sort=False)

    product_payloads_for_update = {"single_products": [], "product_groups": []}
    for name, g in changed_products_gb:
        payload, product_type = _product_update_payload(g)
        product_payloads_for_update[f"{product_type}s"].append(payload)

    return product_payloads_for_update


def _product_update_payload(g):
    product = {}
    g = g.fillna("").to_dict("records")
    r = g[0]
    product.update(
        {
            "id": r["p_id"],
            "inventory_level": r["qty"],
            "sale_price": r["pSale"],
            "price": r["pMAP"],
            "list_on_amazon": r["listOnAmazon"],
            "list_on_ebay": r["listOnEbay"],
            "list_on_walmart": r["listOnWalmart"],
            "amazon_price": r["pAmazon"],
            "retail_price": r["pMSRP"],
            "cf_ebay_category": r["cf_ebay_category"],
            "cf_ebay_price": r["cf_ebay_price"],
            "cf_amazon_status": r["cf_amazon_status"],
            "cf_ebay_status": r["cf_ebay_status"],
            "cf_walmart_status": r["cf_walmart_status"],
        }
    )
    if r["clearance_cat"] != "":
        product.update({"categories": [int(r["cat"]), int(r["clearance_cat"])]})
    else:
        product.update({"categories": [int(r["cat"])]})
    if r["image_0"] != "":
        product.update({"is_visible": True})
    elif r["image_0"] == "":
        product.update({"is_visible": False})
    if len(g) > 1:
        variants = []
        for i, h in enumerate(g[1:]):
            if i == 0:
                product["cf_ebay_category"] = h["cf_ebay_category"]
                product["cf_ebay_price"] = float(h["cf_ebay_price"])
                product["cf_amazon_status"] = h["cf_amazon_status"]
                product["cf_ebay_status"] = h["cf_ebay_status"]
                product["cf_walmart_status"] = h["cf_walmart_status"]
            variant = {}
            variant.update(
                {
                    "id": h["v_id"],
                    "inventory_level": h["qty"],
                    "price": h["pMAP"],
                    "amazon_price": h["pAmazon"],
                    "sale_price": h["pSale"],
                    "retail_price": h["pMSRP"],
                }
            )
            variants.append(variant)
        product.update({"variants": variants})
        return product, "product_group"
    return product, "single_product"


if __name__ == "__main__":
    ready = pd.read_pickle(f"{DATA_DIR}/ready.pkl")
    build_update_payloads(ready)
