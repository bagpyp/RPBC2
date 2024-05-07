import pandas as pd

from src.util import DATA_DIR


def pickles():
    p = pd.read_pickle(f"{DATA_DIR}/products.pkl")

    len(p[p.image_0.notna() & p.v_image_url.notna()])


if __name__ == "__main__":
    pickles()
