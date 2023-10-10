from time import gmtime

from numpy import nan, where

from config import amazon_excluded_vendors
from src.api import get_all_brand_ids, get_all_category_ids, create_brand
from src.constants import to_clearance_map
from src.util.path_utils import DATA_DIR


def prepare_df_for_upload(df):
    df.index.name = "sku"
    df = df.reset_index()

    # fill nulls with native zeros
    df.loc[:, ["p_id", "v_id", "v_image_url", "image_0"]] = df[
        ["p_id", "v_id", "v_image_url", "image_0"]
    ].fillna("")
    df.loc[:, df.select_dtypes(object).columns.tolist()] = df.select_dtypes(
        object
    ).fillna("")
    df.loc[:, df.select_dtypes(int).columns.tolist()] = df.select_dtypes(int).fillna(0)
    df.loc[:, df.select_dtypes(float).columns.tolist()] = df.select_dtypes(
        float
    ).fillna(0)
    df.loc[:, ["p_id", "v_id", "v_image_url", "image_0"]] = df[
        ["p_id", "v_id", "v_image_url", "image_0"]
    ].replace("", nan)

    brand_ids = get_all_brand_ids()
    category_ids = get_all_category_ids()
    for brand in df[~df.BRAND.isin(list(brand_ids.values()))].BRAND.unique():
        brand_ids.update({create_brand(brand): brand})
    df["brand"] = df.BRAND.str.lower().map(
        {v.lower(): str(k) for k, v in brand_ids.items()}
    )
    df["cat"] = df.CAT.map({v: str(k) for k, v in category_ids.items()})

    year = gmtime().tm_year
    month = gmtime().tm_mon
    # only showing last 3 years - (3)
    # winter product becomes old in May - (4)
    # summer product becomes old in November - (11)
    old = [
        f"{n - 1}-{n}"
        for n in range(
            int(str((year + 1) - 3)[2:]) + int(month >= 5),
            int(str(year)[2:]) + int(month >= 5),
        )
    ] + [
        str(i)
        for i in range(
            int(str(year - 3)) + int(month >= 5), int(year) + int(month >= 11)
        )
    ]
    # new = [
    #     f"{(int(str(year)[-2:]) - 1) + int(month > 5)}"
    #     + f"-{(int(str(year)[-2:])) + int(month > 5)}",
    #     f"{year + int(month > 11)}",
    # ]

    df["is_old"] = df.webName.str.contains("|".join(old))
    df["clearance_cat"] = where(
        df.webName.str.contains("|".join(old)), df.cat.map(to_clearance_map), ""
    )

    df = df[df.brand != ""]

    df.pAmazon = df.pAmazon.round(2)

    df["listOnAmazon"] = ~df.BRAND.isin(amazon_excluded_vendors)

    df.to_pickle(f"{DATA_DIR}/ready.pkl")

    return df
