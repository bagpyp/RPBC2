import datetime as dt

from config import update_window_hours
from src.upload.create import product_creation_payload
from src.upload.update import product_update_payload


def build_payloads(df):
    gb = df.groupby("webName")

    new_products_gb = gb.filter(lambda g: g.p_id.count() == 0).groupby(
        "webName", sort=False
    )
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
            product_payloads_for_update.append(product_update_payload(g))
        except Exception:
            print("Couldn't create update payload for", name)
            continue

    product_payloads_for_creation = []
    for name, g in new_products_gb:
        try:
            product_payloads_for_creation.append(product_creation_payload(g))
        except Exception:
            print("Couldn't create creation payload for", name)
            continue

    return product_payloads_for_update, product_payloads_for_creation
