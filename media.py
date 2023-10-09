from glob import glob

import pandas as pd
import requests
from numpy import nan

from util.path_utils import DATA_DIR, IMAGES_DIR


# redefine product data model topology


def lift(g):
    if len(g) > 1:
        fr = g.iloc[[0]].copy()
        fr.sku = "0-" + fr.sku
        fr.loc[:, ["isid", "UPC", "mpn", "alt_color", "size", "color"]] = nan
        fr.loc[
            :,
            [
                "pSale",
                "pMAP",
                "pMSRP",
                "pAmazon",
                "pSWAP",
                "fCreated",
                "lModified",
                "fRcvd",
                "lRcvd",
                "lSold",
            ],
        ] = (
            g.loc[
                :,
                [
                    "pSale",
                    "pMAP",
                    "pMSRP",
                    "pAmazon",
                    "pSWAP",
                    "fCreated",
                    "lModified",
                    "fRcvd",
                    "lRcvd",
                    "lSold",
                ],
            ]
            .max()
            .values
        )
        fr.cost = g.cost.min()
        fr.qty = g.qty.sum()
        g.sku = "1-" + g.sku
        return pd.concat([fr, g])
    else:
        g.sku = "2-" + g.sku
        return g.iloc[[0]]


def configureOptions(df):
    gb = df.reset_index().groupby("webName", sort=False)
    optionDf = pd.concat([lift(g) for _, g in gb]).reset_index()
    return optionDf


# media from BC


def mediate(g):
    if len(g) > 1:
        # lift images to base pane
        g0 = g.iloc[[0]]
        g1 = g.iloc[list(range(1, len(g)))]
        g0.iloc[[0], -5:] = g1.iloc[[0], -5:].values
        g1.loc[:, [f"image_{i}" for i in range(5)]] = nan
        # lift all else p_
        for p in [
            "p_name",
            "p_sku",
            "p_categories",
            "p_description",
            "p_is_visible",
            "p_date_created",
            "p_date_modified",
            "p_id",
            "description",
        ]:
            if g1[p].count():
                g0[p] = g1.loc[g1[p].first_valid_index()][p]
                g1.loc[:, p] = nan
        return pd.concat([g0, g1])
    else:
        g.image_0 = g.image_0.fillna(g.v_image_url)
        g.v_image_url = nan
        return g


def reshapeMedia(df):
    gb = df.groupby("webName", sort=False)
    mdf = pd.concat([mediate(g) for _, g in gb])
    mdf.description = mdf.description.fillna(mdf.p_description)
    return mdf


def archiveMedia(df):
    to_download = {}
    # base images
    bases = [
        b.split("\\")[-1].split(".")[0] for b in glob(f"{IMAGES_DIR}\\base\\*.jpeg")
    ]
    base = (
        df[df.sku.str[:2] != "1-"][["sku"] + [f"image_{i}" for i in range(5)]]
        .set_index("sku")
        .dropna(how="all")
    )
    for name, urls in base.iterrows():
        for i, url in enumerate(urls.dropna().tolist()):
            if name + f"_{i}" not in bases:
                # add this filename, url pair to to_download
                to_download[f"{IMAGES_DIR}/base/" + name + f"_{i}"] = url

    # variant images
    variants = [
        b.split("\\")[-1].split(".")[0] for b in glob(f"{IMAGES_DIR}\\variant\\*.jpeg")
    ]
    variant = (
        df[df.sku.str[:2] == "1-"][["sku", "v_image_url"]]
        .set_index("sku")
        .dropna(how="all")
    )
    for name, url in variant.iterrows():
        if name not in variants:
            # add this filename, url pair to to_download
            to_download[f"{IMAGES_DIR}/variant/" + name] = url.values[0]

    # download step
    for file_path, url in to_download.items():
        with open(file_path + ".jpeg", "wb") as f:
            f.write(requests.get(url).content)

    # picklin' pics
    media = pd.read_pickle(f"{DATA_DIR}/media.pkl")
    media_now = df[
        ["sku", "v_image_url", "description"] + [f"image_{i}" for i in range(5)]
    ].set_index("sku")
    media.update(media_now)
    media = pd.concat([media, media_now[~media_now.index.isin(media.index)]])
    media.to_pickle(f"{DATA_DIR}/media.pkl")


def fileDf():
    v = [g.split("\\")[-1].split(".")[0] for g in glob(f"{IMAGES_DIR}\\variant\\*")]
    b = pd.DataFrame(
        [g.split("\\")[-1].split(".")[0] for g in glob(f"{IMAGES_DIR}\\base\\*")]
    )
    b = (
        b[b[0].str.contains("_")][0]
        .str.split("_", expand=True)[0]
        .value_counts()
        .to_dict()
    )
    files = pd.DataFrame(
        index=list(b.keys()) + v,
        columns=["v_image_url"] + [f"image_{i}" for i in range(5)],
    )
    for sku, _ in files.iterrows():
        if sku in v:
            files.loc[sku, "v_image_url"] = sku + ".jpeg"
        elif sku in b:
            for i in range(b[sku]):
                files.loc[sku, f"image_{i}"] = sku + f"_{i}.jpeg"
    files.columns += "_file"
    files = "/product_images/imported/" + files
    return files
