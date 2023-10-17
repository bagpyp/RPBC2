import pandas as pd

from scripts.quivers import send_to_quivers
from src.upload.create import create_products, build_create_payloads
from src.upload.update import update_products, build_update_payloads
from src.util import DATA_DIR


def upload_ready():
    df = pd.read_pickle(f"{DATA_DIR}/ready.pkl")

    product_payloads_for_update = build_update_payloads(df)
    product_payloads_for_creation = build_create_payloads(df)
    update_products(product_payloads_for_update)
    create_products(product_payloads_for_creation)
    send_to_quivers()


if __name__ == "__main__":
    upload_ready()
