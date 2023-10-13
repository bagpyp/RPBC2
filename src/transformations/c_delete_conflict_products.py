from glob import glob

from tqdm import tqdm

from src.api import delete_product
from src.util.path_utils import DATA_DIR


def delete_conflict_products(df, pdf, delete_conflicts=False):
    df = df.copy()
    pdf = pdf.copy()

    degenerates = pdf[~pdf.p_name.isin(df["webName"])]
    cols = ["p_name", "p_id", "p_sku", "v_sku", "v_id", "v_image_url"] + [
        f"image_{i}" for i in range(5)
    ]
    degenerates = degenerates[cols]

    image_cols = ["v_sku", "v_image_url"] + [f"image_{i}" for i in range(5)]
    images_from_degenerates = degenerates[degenerates["v_image_url"] != ""][image_cols]

    num_degenerates = len(glob(f"{DATA_DIR}/degenerate_images*"))
    images_from_degenerates.to_pickle(
        f"{DATA_DIR}/degenerate_images{num_degenerates}.pkl"
    )

    pdf_changed = False
    if delete_conflicts:
        bad_ids = degenerates.p_id.dropna().unique().tolist()
        for p_id in tqdm(bad_ids):
            delete_product(p_id)
            pdf = pdf[pdf.p_id != p_id]
            pdf_changed = True
        if pdf_changed:
            print("Committing pdf changes to products.pkl")
            pdf.to_pickle(f"{DATA_DIR}/products.pkl")
    return pdf
