import pandas as pd
from numpy import nan

from config import apply_changes
from src.product_images import (
    persist_web_media,
    build_image_locations_from_file_structure,
)
from src.util import DATA_DIR


def _restructure_product_group_media(group):
    if len(group) > 1:
        image_cols = [f"image_{i}" for i in range(5)]
        # lift images to base level of product group
        first_row = group.iloc[[0], :].copy()
        rest_of_group = group.iloc[1:, :].copy()
        rest_of_group.loc[:, image_cols] = nan
        # lift all other product representative data to first row
        # TODO: also lift custom_fields (cf_*) to front row
        #  instead of getting it from rest-of-group later in payloads files.
        #  for both update and create...
        for product_column in [
            "p_name",
            "p_sku",
            "p_categories",
            "p_description",
            "p_is_visible",
            "p_id",
            "p_qty",
            "description",
        ] + [f"image_{i}" for i in range(5)]:
            if rest_of_group[product_column].count():
                first_valid_index = rest_of_group[product_column].first_valid_index()
                first_row.loc[:, product_column] = rest_of_group.loc[
                    first_valid_index, product_column
                ]
                rest_of_group.loc[:, product_column] = nan
        return pd.concat([first_row, rest_of_group])
    else:
        group.image_0 = group.image_0.fillna(group.v_image_url)
        group.v_image_url = nan
        return group


def collect_images_from_product_children(df):
    print("Shuffling images among product group Representatives and Members...")
    gb = df.groupby("webName", sort=False)
    mdf = gb.apply(lambda g: _restructure_product_group_media(g.reset_index(drop=True)))
    mdf = mdf.reset_index(drop=True)
    mdf.description = mdf.description.fillna(mdf.p_description)
    mdf = mdf[~mdf.sku.duplicated(keep=False)]

    if apply_changes:
        persist_web_media(df)
        file_structure_df = build_image_locations_from_file_structure()
    else:
        file_structure_df = pd.read_pickle(f"{DATA_DIR}/file_df.pkl")

    mdf = mdf.set_index("sku").join(file_structure_df)

    mdf.to_pickle(f"{DATA_DIR}/mediated_df.pkl")
    return mdf


if __name__ == "__main__":
    pruned_df = pd.read_pickle(f"{DATA_DIR}/pruned_df.pkl")
    collect_images_from_product_children(pruned_df)
