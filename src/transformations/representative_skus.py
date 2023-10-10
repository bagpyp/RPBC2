import pandas as pd
from numpy import nan


def _restructure_product_group(g):
    if len(g) > 1:
        fr = g.iloc[[0]].copy()
        fr.sku = "0-" + fr.sku
        fr.loc[:, ["isid", "UPC", "mpn", "alt_color", "size", "color"]] = nan
        fr.loc[
            :,
            [
                "pSale",
                "pMAP",
                "pMSRP",
                "pAmazon",
                "pSWAP",
                "fCreated",
                "lModified",
                "fRcvd",
                "lRcvd",
                "lSold",
            ],
        ] = (
            g.loc[
                :,
                [
                    "pSale",
                    "pMAP",
                    "pMSRP",
                    "pAmazon",
                    "pSWAP",
                    "fCreated",
                    "lModified",
                    "fRcvd",
                    "lRcvd",
                    "lSold",
                ],
            ]
            .max()
            .values
        )
        fr.cost = g.cost.min()
        fr.qty = g.qty.sum()
        g.sku = "1-" + g.sku
        return pd.concat([fr, g])
    else:
        g.sku = "2-" + g.sku
        return g.iloc[[0]]


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
