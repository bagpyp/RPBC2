from numpy import nan

from config import apply_changes
from src.api.products import delete_product
from src.util import DATA_DIR


def delete_conflict_products(df):
    df = df.copy()

    # products whose variant sku doesn't exist in retail pro, shouldn't exist in big commerce
    dangling_variants = df[df.sku.isna()]
    bad_ids = dangling_variants[dangling_variants.p_id.notna()].p_id.unique().tolist()

    # after the following line, it's like we did a left join, not outer onw
    df = df[df.sku.notna()]

    full_carryovers = df[(~df.p_name.isin(df.webName)) & df.p_name.notna()]
    bad_ids += full_carryovers[full_carryovers.p_id.notna()].p_id.unique().tolist()

    # merge conflicts
    misshaped_groups = df.groupby("webName").filter(
        lambda g: len(g) > g.v_sku.count() + 1
    )
    bad_ids += misshaped_groups[misshaped_groups.p_id.notna()].p_id.unique().tolist()

    partial_carryovers = df.groupby("p_name").filter(lambda g: g.webName.nunique() > 1)
    bad_ids += (
        partial_carryovers[partial_carryovers.p_id.notna()].p_id.unique().tolist()
    )

    if apply_changes:
        for p_id in list(set(bad_ids)):
            delete_product(p_id)

    # TODO: store column lists as constants
    web_cols = [
        "p_name",
        "p_sku",
        "v_sku",
        "p_categories",
        "p_description",
        "v_image_url",
        "p_is_visible",
        "p_id",
        "v_id",
        "p_qty",
        "v_qty",
        "cf_ebay_category",
        "cf_ebay_price",
        "cf_amazon_status",
        "cf_ebay_status",
        "cf_walmart_status",
    ] + [f"image_{i}" for i in range(5)]

    df.loc[df.p_id.isin(bad_ids), web_cols] = nan

    df.to_pickle(f"{DATA_DIR}/pruned_df.pkl")
    return df


if __name__ == "__main__":
    import pandas as pd

    merged_df = pd.read_pickle(f"{DATA_DIR}/merged_df.pkl")
    delete_conflict_products(merged_df)
