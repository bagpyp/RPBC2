import pandas as pd
from numpy import nan

from config import apply_changes
from src.api.products import delete_product
from src.util import DATA_DIR


def attach_web_data_to_products(df, pdf):
    df = df.copy()
    pdf = pdf.copy()
    df = df[~df.sku.duplicated(keep=False)]

    # LZ for 5 image columns
    for i in range(5):
        if f"image_{i}" not in pdf:
            pdf[f"image_{i}"] = nan

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
    ] + [f"image_{i}" for i in range(5)]

    pdf = pdf[pdf.v_sku.replace("", nan).notna()][web_cols]

    df = pd.merge(df, pdf, how="left", left_on="sku", right_on="v_sku").replace("", nan)

    # merge conflicts
    degenerate_df = df.groupby("webName").filter(lambda g: len(g) > g.v_sku.count() + 1)
    bad_ids = degenerate_df[degenerate_df.p_id.notna()].p_id.unique().tolist()

    if apply_changes:
        for p_id in bad_ids:
            delete_product(p_id)

    df.loc[df.p_id.isin(bad_ids), web_cols] = nan

    df.to_pickle(f"{DATA_DIR}/merged_df.pkl")
    return df


if __name__ == "__main__":
    option_df = pd.read_pickle(f"{DATA_DIR}/option_df.pkl")
    products = pd.read_pickle(f"{DATA_DIR}/products.pkl")

    df = attach_web_data_to_products(option_df, products)
    print(df)
    gb = df.groupby("webName")
