# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:22:09 2020

@author: Web
"""

from glob import glob
from numpy import nan
import pandas as pd
import requests
import time
import tqdm


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
    print("configuring product options...")
    time.sleep(0.69)
    gb = df.reset_index().groupby("webName", sort=False)
    optionDf = pd.concat([lift(g) for _, g in tqdm.tqdm(gb)]).reset_index()
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
    gs = [mediate(g) for _, g in tqdm.tqdm(gb)]
    mdf = pd.concat(gs)
    mdf.description = mdf.description.fillna(mdf.p_description)
    mdf.to_pickle("mediatedDf.pkl")
    return mdf


def download(url, name):
    with open(name + ".jpeg", "wb") as f:
        f.write(requests.get(url).content)


def archiveMedia(df):
    # base images
    bases = [b.split("\\")[-1].split(".")[0] for b in glob("images\\base\\*.jpeg")]
    base = (
        df[df.sku.str[:2] != "1-"][["sku"] + [f"image_{i}" for i in range(5)]]
        .set_index("sku")
        .dropna(how="all")
    )
    for name, urls in base.iterrows():
        for i, url in enumerate(urls.dropna().tolist()):
            if name + f"_{i}" not in bases:
                download(url, "images/base/" + name + f"_{i}")

    # variant images
    variants = [
        b.split("\\")[-1].split(".")[0] for b in glob("images\\variant\\*.jpeg")
    ]
    variant = (
        df[df.sku.str[:2] == "1-"][["sku", "v_image_url"]]
        .set_index("sku")
        .dropna(how="all")
    )
    print("donwloading new pictures to archive...")
    for name, url in tqdm.tqdm(variant.iterrows()):
        if name not in variants:
            download(url.values[0], "images/variant/" + name)

    # picklin' pics
    media = pd.read_pickle("data/media.pkl")
    media_now = df[
        ["sku", "v_image_url", "description"] + [f"image_{i}" for i in range(5)]
    ].set_index("sku")
    media.update(media_now)
    media = pd.concat([media, media_now[~media_now.index.isin(media.index)]])
    media.to_pickle("data/media.pkl")


def fileDf():
    v = [g.split("\\")[-1].split(".")[0] for g in glob("images\\variant\\*")]
    b = pd.DataFrame([g.split("\\")[-1].split(".")[0] for g in glob("images\\base\\*")])
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
