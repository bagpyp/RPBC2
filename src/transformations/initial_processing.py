import pandas as pd

from src.data_maps import category_map


def clean_and_filter(df):
    # nuke duplicate SKUs
    df = df[~df.sku.duplicated(keep=False)]

    # just to make sure we have all the UPCs
    df.UPC = df.UPC.fillna(df.UPC2)
    df.drop(columns="UPC2", inplace=True)

    # formatting columns
    for i in range(12, 18):
        df.iloc[:, i] = df.iloc[:, i].map(pd.to_numeric)

    # bad solution
    df.lModified = df.lModified.astype(str).str[:-6]
    for i in range(18, 23):
        df.iloc[:, i] = df.iloc[:, i].map(
            lambda x: pd.to_datetime(x, format="%Y-%m-%dT%H:%M:%S")
        )

    for i in range(23, 29):
        df.iloc[:, i] = (
            df.iloc[:, i].fillna("0").astype(int).map(lambda x: 0 if x < 0 else x)
        )

    # ATTN: setting qty to only store quantity (qty1)
    df.qty = df.qty1
    # keeping old DCS name
    df["DCSname"] = df.CAT.values

    # drop rental, service and used product (not clearance)
    df = df[~df.DCS.str.match(r"(SER|REN|USD)")]

    # map the rest of the categories, map null to Misc
    df.CAT = df.CAT.map(category_map).fillna("Misc")

    # filters products without UPCs w/ length 11, 12 or 13.
    df = df[df.UPC.str.len().isin([11, 12, 13])]

    # map null brands to Hillcrest
    df.BRAND = df.BRAND.str.strip().str.replace("^$", "Hillcrest", regex=True)

    df.sku = df.sku.astype(int)
    df = df.sort_values(by="sku")
    df.sku = df.sku.astype(str).str.zfill(5)
    df.set_index("sku", drop=True, inplace=True)
    df = df[df["name"].notna()]
    df["webName"] = (df.name.str.title() + " " + df.year.fillna("")).str.strip()

    # settling webNames with more than one ssid
    chart = df[["webName", "ssid"]].groupby("ssid").first().sort_values(by="webName")
    j = 0
    for i in range(1, len(chart)):
        if chart.iloc[i, 0] != chart.iloc[i - (j + 1), 0]:
            j = 0
        else:
            chart.iloc[i, 0] += f" {j + 1}"
            j += 1
    df.webName = df.ssid.map(chart.webName.to_dict())
