from glob import glob

import pandas as pd
import requests

from src.util import IMAGES_DIR, DATA_DIR


def persist_web_media(df):
    to_download = {}
    # base images
    bases = [
        b.split("\\")[-1].split(".")[0] for b in glob(f"{IMAGES_DIR}\\base\\*.jpeg")
    ]
    # contains 0-s and 2-s
    """
    bases[:5]
    ['0-00001_0', '0-00001_1', '0-00002_0', '0-00004_0', '0-00004_1']
    """
    base = (
        df[df.sku.str[:2] != "1-"][["sku"] + [f"image_{i}" for i in range(5)]]
        .set_index("sku")
        .dropna(how="all")
    )
    # all index values start with 2-
    """
    base.sample(5)
                                                        image_0  ...                                            image_4
    sku                                                          ...                                                   
    2-120463  https://cdn11.bigcommerce.com/s-gaywsgumtw/pro...  ...  https://cdn11.bigcommerce.com/s-gaywsgumtw/pro...
    2-43108   https://cdn11.bigcommerce.com/s-gaywsgumtw/pro...  ...                                                NaN
    2-08613   https://cdn11.bigcommerce.com/s-gaywsgumtw/pro...  ...                                                NaN
    2-35747   https://cdn11.bigcommerce.com/s-gaywsgumtw/pro...  ...                                                NaN
    2-53466   https://cdn11.bigcommerce.com/s-gaywsgumtw/pro...  ...                                                NaN
    """
    for sku, urls in base.iterrows():
        for i, url in enumerate(urls.dropna().tolist()):
            sku_image = sku + f"_{i}"
            #  if "2-00045_0" not in bases
            if sku_image not in bases:
                # add this filename, url pair to to_download
                to_download[f"{IMAGES_DIR}/base/" + sku_image] = url

    # variant images
    variants = [
        b.split("\\")[-1].split(".")[0] for b in glob(f"{IMAGES_DIR}\\variant\\*.jpeg")
    ]
    variant = (
        df[df.sku.str[:2] == "1-"][["sku", "v_image_url"]]
        .set_index("sku")
        .dropna(how="all")
    )
    for sku, url in variant.iterrows():
        if sku not in variants:
            # add this filename, url pair to to_download
            to_download[f"{IMAGES_DIR}/variant/" + sku] = url.values[0]

    # download step
    num_new_images = len(to_download)
    if num_new_images:
        print(f"Archiving {num_new_images} images from BigCommerce")
        for file_path, url in to_download.items():
            with open(file_path + ".jpeg", "wb") as f:
                f.write(requests.get(url).content)

    # pickling pics
    media = pd.read_pickle(f"{DATA_DIR}/media.pkl")
    media_now = df[
        ["sku", "v_image_url", "description"] + [f"image_{i}" for i in range(5)]
    ].set_index("sku")
    media.update(media_now)
    media = pd.concat([media, media_now[~media_now.index.isin(media.index)]])
    media.to_pickle(f"{DATA_DIR}/media.pkl")


if __name__ == "__main__":
    mediated_df = pd.read_pickle(f"{DATA_DIR}/mediated_df.pkl")
    persist_web_media(mediated_df)
