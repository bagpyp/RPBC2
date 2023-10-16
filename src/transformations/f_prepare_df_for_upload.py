import json
from time import gmtime

from numpy import nan, where

from config import apply_changes
from src.api import create_brand
from src.constants import amazon_excluded_vendors, to_clearance_map
from src.util import DATA_DIR


def prepare_df_for_upload(df):
    df = df.copy()
    df.index.name = "sku"
    df = df.reset_index()

    # fill nulls with native zeros TODO: why??
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

    # BRANDS
    """
    "5909": "Snow Angel",
    "5910": "BENTMETAL",
    "5911": "Kulkea SMC",
    """
    with open(f"{DATA_DIR}/brand_ids.json") as brand_file:
        brand_ids = json.load(brand_file)
        brand_ids = {int(k): v for k, v in brand_ids.items()}

    bigcommerce_brand_names = [b.lower() for b in list(brand_ids.values())]
    new_brands = df[~df.BRAND.str.lower().isin(bigcommerce_brand_names)].BRAND.unique()

    for new_brand in new_brands:
        if apply_changes:
            new_brand_response = create_brand(new_brand)
            if new_brand_response.ok:
                new_brand_id = new_brand_response.json()["data"]["id"]
                brand_ids.update({str(new_brand_id): new_brand})

    df["brand"] = df.BRAND.str.lower().map(
        {v.lower(): str(k) for k, v in brand_ids.items()}
    )

    # CATEGORIES
    """    
    "6914": "Ski/Poles",
    "7011": "Ski/Poles/Adult",
    "6915": "Ski/Poles/Youth",
    """
    with open(f"{DATA_DIR}/category_ids.json") as category_file:
        category_ids = json.load(category_file)
    df["cat"] = df.CAT.map({v: k for k, v in category_ids.items()})

    year = gmtime().tm_year
    month = gmtime().tm_mon

    # only showing last 3 years - (3)
    # winter product becomes old in May - (4)
    # summer product becomes old in November - (11)
    old = [
        f" {n - 1}-{n}$"
        for n in range(
            int(str((year + 1) - 3)[2:]) + int(month >= 5),
            int(str(year)[2:]) + int(month >= 5),
        )
    ] + [
        f" {i}$"
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
