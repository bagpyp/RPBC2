import pandas as pd
from tqdm import tqdm

from src.api.products import update_product
from src.util import DATA_DIR


def pickles():
    p = pd.read_pickle(f"{DATA_DIR}/products.pkl")

    pids = p[~p.p_is_visible & p.p_qty > 0].p_id.unique()
    for pid in tqdm(pids):
        update_product(pid, {"is_visible": True})


if __name__ == "__main__":
    pickles()
