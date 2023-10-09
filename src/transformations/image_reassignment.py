import pandas as pd
from numpy import nan


def _restructure_product_group_media(g):
    if len(g) > 1:
        # lift images to base level of product group
        g0 = g.iloc[[0]]
        g1 = g.iloc[list(range(1, len(g)))]
        g0.iloc[[0], -5:] = g1.iloc[[0], -5:].values
        g1.loc[:, [f"image_{i}" for i in range(5)]] = nan
        # lift all else p_
        for p in [
            "p_name",
            "p_sku",
            "p_categories",
            "p_description",
            "p_is_visible",
            "p_date_created",
            "p_date_modified",
            "p_id",
            "description",
        ]:
            if g1[p].count():
                g0[p] = g1.loc[g1[p].first_valid_index()][p]
                g1.loc[:, p] = nan
        return pd.concat([g0, g1])
    else:
        g.image_0 = g.image_0.fillna(g.v_image_url)
        g.v_image_url = nan
        return g


def collect_images_from_product_children(df):
    gb = df.groupby("webName", sort=False)
    mdf = pd.concat([_restructure_product_group_media(g) for _, g in gb])
    mdf.description = mdf.description.fillna(mdf.p_description)
    return mdf
