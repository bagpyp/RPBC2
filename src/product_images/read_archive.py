from glob import glob

import pandas as pd

from src.util.path_utils import IMAGES_DIR


def build_image_locations_from_file_structure():
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
