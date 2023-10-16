import pandas as pd
from numpy import nan

from src.util import DATA_DIR


def _restructure_product_group(group):
    if len(group) > 1:
        header_row = group.iloc[[0]].copy()
        header_row.sku = "0-" + header_row.sku

        item_cols = ["isid", "UPC", "mpn", "alt_color", "size", "color"]
        price_cols = ["pSale", "pMAP", "pMSRP", "pAmazon", "pSWAP"]
        date_cols = ["fCreated", "lModified", "fRcvd", "lRcvd", "lSold"]

        header_row.loc[:, item_cols] = nan
        header_row.loc[:, price_cols] = group.loc[:, price_cols].max().values
        header_row.loc[:, date_cols] = group.loc[:, date_cols].max().values

        header_row.cost = group.cost.min()
        header_row.qty = group.qty.sum()

        group.sku = "1-" + group.sku

        return pd.concat([header_row, group])
    else:
        group.sku = "2-" + group.sku
        return group.iloc[[0]]


def build_product_group_structure(df):
    print("Building Representative SKUs and Product Options Structure..")
    df = df.copy()
    gb = df.reset_index().groupby("webName", sort=False)

    dfs = []
    for _, group in gb:
        dfs.append(_restructure_product_group(group))

    df_with_options = pd.concat(dfs).reset_index()
    column_order = [
        "webName",
        "sku",
        "UPC",
        "CAT",
        "DCSname",
        "BRAND",
        "name",
        "mpn",
        "size",
        "color",
        "qty",
        "cost",
        "pSale",
        "pMAP",
        "pMSRP",
        "pAmazon",
        "fCreated",
        "lModified",
        "description",
    ]
    result = df_with_options[column_order]
    result.to_pickle(f"{DATA_DIR}/option_df.pkl")
    return result
