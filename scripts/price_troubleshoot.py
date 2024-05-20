import pandas as pd

from src.util import DATA_DIR


def main():
    pd.options.display.max_rows = 1000
    pd.options.display.max_columns = 100
    pd.options.display.width = 300

    ready = pd.read_pickle(f"{DATA_DIR}/ready.pkl")

    problems = ready[ready.cf_ebay_price != ready.pAmazon]

    debug = True


if __name__ == "__main__":
    main()
