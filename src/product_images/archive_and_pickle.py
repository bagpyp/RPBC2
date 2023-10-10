from glob import glob

import pandas as pd
import requests

from src.util.path_utils import IMAGES_DIR, DATA_DIR


def persist_web_media(df):
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
    num_new_images = len(to_download)
    if num_new_images:
        print(f"Archiving {num_new_images} images from BigCommerce")
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
