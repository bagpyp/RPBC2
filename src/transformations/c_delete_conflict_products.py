from config import apply_changes
from src.api.products import delete_product
from src.util import DATA_DIR


def delete_conflict_products(df, pdf):
    df = df.copy()
    pdf = pdf.copy()

    # this deletes products on the web that have been entirely carried over in retail pro,
    # meaning that the desc1/desc2 no longer exists in retail pro, so webName won't map back
    degenerates = pdf[~pdf.p_name.isin(df["webName"])]
    cols = ["p_name", "p_id", "p_sku", "v_sku", "v_id", "v_image_url"] + [
        f"image_{i}" for i in range(5)
    ]
    degenerates = degenerates[cols]

    # image_cols = ["v_sku", "v_image_url"] + [f"image_{i}" for i in range(5)]
    # TODO: use this df to download images into images/variant
    #  (replace 0- or 2- with 1-) before deleting the product
    #  because that also deletes the images! ask Ryan Steffey
    # images_from_degenerates = degenerates[degenerates["v_image_url"] != ""][image_cols]

    if apply_changes:
        pdf_changed = False
        bad_ids = degenerates.p_id.dropna().unique().tolist()
        for p_id in bad_ids:
            delete_product(p_id)
            pdf = pdf[pdf.p_id != p_id]
            pdf_changed = True
        if pdf_changed:
            pdf.to_pickle(f"{DATA_DIR}/products.pkl")
    return pdf


if __name__ == "__main__":
    import pandas as pd

    pickle_df = pd.read_pickle(f"{DATA_DIR}/option_df.pkl")
    pickle_pdf = pd.read_pickle(f"{DATA_DIR}/products.pkl")

    new_pickle_pdf = delete_conflict_products(pickle_df, pickle_pdf)
