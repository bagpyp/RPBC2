import pandas as pd
from numpy import nan


def _restructure_product_group(product_group):
    if len(product_group) > 1:
        header_product_row = product_group.iloc[[0]].copy()
        header_product_row.sku = "0-" + header_product_row.sku
        header_product_row.loc[
            :, ["isid", "UPC", "mpn", "alt_color", "size", "color"]
        ] = nan
        price_cols = ["pSale", "pMAP", "pMSRP", "pAmazon", "pSWAP"]
        date_cols = ["fCreated", "lModified", "fRcvd", "lRcvd", "lSold"]
        header_product_row.loc[:, price_cols] = (
            product_group.loc[:, price_cols].max().values
        )
        header_product_row.loc[:, date_cols] = (
            product_group.loc[:, date_cols].max().values
        )
        header_product_row.cost = product_group.cost.min()
        header_product_row.qty = product_group.qty.sum()
        product_group.sku = "1-" + product_group.sku
        return pd.concat([header_product_row, product_group])
    else:
        product_group.sku = "2-" + product_group.sku
        return product_group.iloc[[0]]


def build_product_group_structure(df):
    gb = df.reset_index().groupby("webName", sort=False)
    df_with_options = pd.concat(
        [_restructure_product_group(g) for _, g in gb]
    ).reset_index()
    df_with_options = df_with_options[
        [
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
    ]
    return df_with_options
