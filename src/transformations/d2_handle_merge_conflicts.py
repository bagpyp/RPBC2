import pandas as pd

from src.util import DATA_DIR


def handle_merge_conflicts(df):
    pass


if __name__ == "__main__":
    pickle_df = pd.read_pickle(f"{DATA_DIR}/merged_df.pkl")
    handle_merge_conflicts(pickle_df)
