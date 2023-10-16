from tqdm import tqdm

from config import apply_changes
from src.api.products import delete_product
from src.util import DATA_DIR


def delete_conflict_products(df, pdf):
    df = df.copy()
    pdf = pdf.copy()

    degenerates = pdf[~pdf.p_name.isin(df["webName"])]
    cols = ["p_name", "p_id", "p_sku", "v_sku", "v_id", "v_image_url"] + [
        f"image_{i}" for i in range(5)
    ]
    degenerates = degenerates[cols]

    image_cols = ["v_sku", "v_image_url"] + [f"image_{i}" for i in range(5)]
    # TODO: use this df to download images into images/variant
    #  (replace 0- or 2- with 1-) before deleting the product
    #  because that also deletes the images! ask ryan steffey
    # images_from_degenerates = degenerates[degenerates["v_image_url"] != ""][image_cols]

    if apply_changes:
        pdf_changed = False
        bad_ids = degenerates.p_id.dropna().unique().tolist()
        for p_id in tqdm(bad_ids):
            delete_product(p_id)
            pdf = pdf[pdf.p_id != p_id]
            pdf_changed = True
        if pdf_changed:
            pdf.to_pickle(f"{DATA_DIR}/products.pkl")
    return pdf
