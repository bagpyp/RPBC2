import pandas as pd

from config import sync_sideline_swap
from src.server import write_orders_to_ecm
from src.util.path_utils import INVOICES_DIR
from .get_all import get_all_orders, get_all_returns


def process_orders_and_returns():
    all_new_orders = get_all_orders(sync_sideline_swap)
    write_orders_to_ecm(all_new_orders)

    written_receipts = pd.read_csv(f"{INVOICES_DIR}/written.csv")
    written_receipt_ids = written_receipts.comment1.apply(
        lambda x: x.split(" ")[1]
    ).tolist()
    all_new_returns = get_all_returns(sync_sideline_swap)
    write_orders_to_ecm(
        [ret for ret in all_new_returns if str(ret.get("id")) in written_receipt_ids],
        # meaning the receipt is of type `return`
        regular=False,
    )
