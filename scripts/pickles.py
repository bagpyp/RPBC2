import pandas as pd

from src.util import DATA_DIR


def pickles():
    clean_df = pd.read_pickle(f"{DATA_DIR}/clean_df.pkl")
    fileDf = pd.read_pickle(f"{DATA_DIR}/fileDf.pkl")
    fromECM = pd.read_pickle(f"{DATA_DIR}/fromECM.pkl")
    mediated_df = pd.read_pickle(f"{DATA_DIR}/mediated_df.pkl")
    merged_df = pd.read_pickle(f"{DATA_DIR}/merged_df.pkl")
    option_df = pd.read_pickle(f"{DATA_DIR}/option_df.pkl")
    products = pd.read_pickle(f"{DATA_DIR}/products.pkl")
    ready = pd.read_pickle(f"{DATA_DIR}/ready.pkl")

    print("have some pickles!")


if __name__ == "__main__":
    pickles()
