import datetime as dt

from config import update_window_hours


def build_update_payloads(df):
    gb = df.groupby("webName")

    changed_products_gb = gb.filter(
        lambda g: (
            g.lModified.max()
            > (dt.datetime.now() - dt.timedelta(hours=update_window_hours))
        )
        & (g.p_id.count() == 1)
    ).groupby("webName", sort=False)

    product_payloads_for_update = []
    for name, g in changed_products_gb:
        try:
            product_payloads_for_update.append(_product_update_payload(g))
        except Exception:
            print("Couldn't create update payload for", name)
            continue

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
            "amazon_price": r["pAmazon"],
            "retail_price": r["pMSRP"],
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
        for h in g[1:]:
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
    return product