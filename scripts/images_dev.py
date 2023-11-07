import pandas as pd
from numpy import nan

from src.util import DATA_DIR

pd.options.display.width = 230
pd.options.display.max_columns = 50
pd.options.display.max_rows = 200
pd.options.display.max_colwidth = 0

mdf = pd.read_pickle(f"{DATA_DIR}/mediated_df.pkl").reset_index()
base_image_cols = [f"image_{i}" for i in range(5)]
image_cols = ["v_image_url"] + base_image_cols
mdf_cols = ["sku", "webName"] + image_cols
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
for i, bic in enumerate(base_image_cols):
    mdf[f"{bic}_id"] = (
        mdf[bic].fillna("").apply(lambda x: int(x.split("/")[2]) if x != "" else 0)
    )
    mdf[f"{bic}_pid"] = (
        mdf[bic].fillna("").apply(lambda x: int(x.split("/")[0]) if x != "" else 0)
    )
    mdf[bic] = (
        mdf[bic]
        .fillna("")
        .apply(lambda x: "".join(x.split("/")[3:]).replace("?c=1", ""))
    )

dav = pd.read_csv(f"{DATA_DIR}/dav.csv")
dav = dav.loc[dav.filename.str[:2].isin(["0-", "2-"]), :]
dav = dav.loc[dav.number != "imported", :]
dav["sku"] = dav.filename.apply(lambda x: x.split("_")[0])
dav = dav[dav.sku.str.match("^\d-\d{5,6}$")]
dav = dav.groupby("sku").filter(lambda g: len(g) <= 10)

pdf = pd.read_pickle(f"{DATA_DIR}/products.pkl")
pdf = pdf[
    [
        "p_id",
        "p_name",
        "p_sku",
        "v_sku",
        "p_is_visible",
        "v_image_url",
        "image_0",
        "image_1",
        "image_2",
        "image_3",
        "image_4",
        "image_5",
        "image_6",
        "image_7",
        "image_8",
        "image_9",
        "image_10",
    ]
]

fdf = pd.read_pickle(f"{DATA_DIR}/fileDf.pkl").apply(
    lambda c: c.str.replace("/product_images/imported/", "").str.replace(".jpeg", "")
)


df = pd.read_pickle(f"{DATA_DIR}/ready.pkl")
info_cols = ["webName", "p_id", "p_sku", "v_sku", "sku"]
df_cols = info_cols + image_cols + [f"{ic}_file" for ic in image_cols]
df = df[df_cols]
reps = df[df.image_0.isna() & ~df.sku.str.startswith("1-")]


debug = True
