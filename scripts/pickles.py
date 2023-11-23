import pandas as pd

from src.util import DATA_DIR


def pickles():
    clean_df = pd.read_pickle(f"{DATA_DIR}/clean_df.pkl")
    file_df = pd.read_pickle(f"{DATA_DIR}/file_df.pkl")
    from_ecm = pd.read_pickle(f"{DATA_DIR}/from_ecm.pkl")
    mediated_df = pd.read_pickle(f"{DATA_DIR}/mediated_df.pkl")
    merged_df = pd.read_pickle(f"{DATA_DIR}/merged_df.pkl")
    option_df = pd.read_pickle(f"{DATA_DIR}/option_df.pkl")
    products = pd.read_pickle(f"{DATA_DIR}/products.pkl")
    ready = pd.read_pickle(f"{DATA_DIR}/ready.pkl")

    cols = ["webName", "sku", "qty", "p_qty", "v_qty"]
    r = ready[cols]
    r = r.groupby("webName").filter(lambda g: g.p_qty.sum() != 0)
    r.loc[r.sku.str[0].isin(["1", "2"]), "p_qty"] = r.loc[
        r.sku.str[0].isin(["1", "2"]), "v_qty"
    ]
    r.drop("v_qty", axis=1, inplace=True)
    print("have some pickles!")


if __name__ == "__main__":
    pickles()
