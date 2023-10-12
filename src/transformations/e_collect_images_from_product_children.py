import pandas as pd
from numpy import nan


def _restructure_product_group_media(group):
    group = group.copy()
    if len(group) > 1:
        # lift images to base level of product group
        first_row = group.iloc[[0]]
        rest_of_group = group.iloc[list(range(1, len(group)))]
        first_row.iloc[[0], -5:] = rest_of_group.iloc[[0], -5:].values
        rest_of_group.loc[:, [f"image_{i}" for i in range(5)]] = nan
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
            if rest_of_group[p].count():
                first_row.loc[:, p] = rest_of_group.loc[
                    rest_of_group[p].first_valid_index()
                ][p]
                rest_of_group.loc[:, p] = nan
        return pd.concat([first_row, rest_of_group])
    else:
        group.image_0 = group.image_0.fillna(group.v_image_url)
        group.v_image_url = nan
        return group


def collect_images_from_product_children(df):
    print("Shuffling images among product group Representatives and Members...")
    gb = df.groupby("webName", sort=False)
    mdf = pd.concat([_restructure_product_group_media(g) for _, g in gb])
    mdf.description = mdf.description.fillna(mdf.p_description)
    mdf = mdf[~mdf.sku.duplicated(keep=False)]
    return mdf
