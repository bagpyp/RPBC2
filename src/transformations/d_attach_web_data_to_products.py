import pandas as pd
from numpy import nan

from src.util import DATA_DIR


def attach_web_data_to_products(df, pdf):
    df = df.copy()
    pdf = pdf.copy()
    df = df[~df.sku.duplicated(keep=False)]

    # LZ for 5 image columns
    for i in range(5):
        if f"image_{i}" not in pdf:
            pdf[f"image_{i}"] = nan

    pdf = pdf[pdf.v_sku.replace("", nan).notna()][
        [
            "p_name",
            "p_sku",
            "v_sku",
            "p_categories",
            "p_description",
            "v_image_url",
            "p_is_visible",
            "p_id",
            "v_id",
            "cf_ebay_category",
            "cf_ebay_price",
            "cf_amazon_status",
        ]
        + [f"image_{i}" for i in range(5)]
    ]

    df = pd.merge(df, pdf, how="left", left_on="sku", right_on="v_sku").replace("", nan)
    df.to_pickle(f"{DATA_DIR}/merged_df.pkl")
    return df


if __name__ == "__main__":
    pickle_df = pd.read_pickle(f"{DATA_DIR}/option_df.pkl")
    pickle_pdf = pd.read_pickle(f"{DATA_DIR}/products.pkl")

    merged_df = attach_web_data_to_products(pickle_df, pickle_pdf)
