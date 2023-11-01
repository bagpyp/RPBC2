import pandas as pd
from numpy import nan

from src.util import DATA_DIR

mdf = pd.read_pickle(f"{DATA_DIR}/media.pkl").reset_index()

base_image_cols = [f"image_{i}" for i in range(5)]
image_cols = ["v_image_url"] + base_image_cols
mdf_cols = ["sku"] + image_cols + ["description"]
mdf = mdf.loc[
    (
        (mdf.image_0.notna() & ~mdf.sku.str.startswith("1-"))
        | (mdf.v_image_url.notna() & mdf.sku.str.startswith("1-"))
    ),
    mdf_cols,
]

mdf["v_image_url"] = mdf["v_image_url"].str.replace(
    "https://cdn11.bigcommerce.com/s-gaywsgumtw/product_images/attribute_rule_images/",
    "",
)
for ic in base_image_cols:
    mdf[ic] = mdf[ic].str.replace(
        "https://cdn11.bigcommerce.com/s-gaywsgumtw/products/", ""
    )
mdf["p_id"] = nan
mdf[[f"{bic}_id" for bic in base_image_cols]] = nan
# for _, row in mdf.iterrows():
#     for i in range(5):
#         row


fdf = pd.read_pickle(f"{DATA_DIR}/fileDf.pkl").apply(
    lambda c: c.str.replace("/product_images/imported/", "").str.replace(".jpeg", "")
)


# 1. Function to split the string
def split_image_path(path):
    if pd.isna(path):
        return None, None
    left, right = path.split("/images/")
    return left, right.split("/")[0]


# 2. Apply the function and store in new dataframes
left_ids_df = pd.DataFrame()
right_ids_df = pd.DataFrame()

for col in base_image_cols:
    mdf[col + "_left"], mdf[col + "_right"] = zip(*mdf[col].map(split_image_path))
    left_ids_df[col + "_left"] = mdf[col + "_left"]
    right_ids_df[col + "_right"] = mdf[col + "_right"]

# 3. Check if the left ids are the same across all columns for each row
mdf["left_same"] = left_ids_df.apply(
    lambda row: len(row.dropna().unique()) == 1, axis=1
)

print(mdf)

df = pd.read_pickle(f"{DATA_DIR}/ready.pkl")
info_cols = ["webName", "p_id", "p_sku", "v_sku", "sku"]
df_cols = info_cols + image_cols + [f"{ic}_file" for ic in image_cols]
df = df[df_cols]

debug = True
