import pandas as pd
from numpy import nan


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
            "p_date_created",
            "p_date_modified",
            "p_id",
            "v_id",
        ]
        + [f"image_{i}" for i in range(5)]
    ]

    df = pd.merge(df, pdf, how="left", left_on="sku", right_on="v_sku").replace("", nan)

    return df
