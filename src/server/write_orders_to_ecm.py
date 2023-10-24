import json
import os
import time

import pandas as pd

from src.server.invoice.invoice import Invoice
from src.util import DATA_DIR, INVOICES_DIR


def _sid():
    sid = str(int(hash(str(time.time())) % 1e13))
    time.sleep(0.1)
    return sid


def read_order_number(regular=True):
    kind = "order" if regular else "return"
    with open(f"{INVOICES_DIR}/base_{kind}_number.txt") as number_file:
        return int(number_file.read())


def overwrite_order_number(new_order_num: int, regular=True):
    kind = "order" if regular else "return"
    with open(f"{INVOICES_DIR}/base_{kind}_number.txt", "w") as number_file:
        number_file.write(str(new_order_num))


def count_written_orders(regular=True):
    kind = "order" if regular else "return"
    order_counts = 0
    for api_source in ["sls", "bc"]:
        with open(f"{DATA_DIR}/{api_source}_{kind}s.json") as f:
            order_counts += len(json.load(f))
    return order_counts


def write_orders_to_ecm(orders, regular=True):
    if len(orders) == 0:
        return

    kind = "orders" if regular else "returns"
    print(f"Found {len(orders)} {kind} online")

    written_receipts = pd.read_csv(f"{INVOICES_DIR}/written.csv")
    written_receipt_numbers = written_receipts.invc_no.unique().tolist()
    order_counts = count_written_orders(regular=regular)

    order_file_number_changed = False
    base_order_number = read_order_number(regular=regular)

    invoices = []
    for i, order in enumerate(orders):
        # TODO: eventually the order numbers will collide with the return numbers.
        order_number = base_order_number + order_counts + (i + 1)
        # adding zero would duplicate receipt # on first iteration, thus (i + 1) above
        while order_number in written_receipt_numbers:
            base_order_number += 1
            order_file_number_changed = True
            order_number = base_order_number + order_counts + (i + 1)
        invoices.append(Invoice(order, order_number, regular=regular))

        if order_file_number_changed:
            overwrite_order_number(base_order_number, regular=regular)

    header = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<!-- Created on {time.strftime("%Y-%m-%dT%H:%M:%S")}-08:00 -->\n'
        f"<!-- V9 STATION -->\n"
        f"<DOCUMENT>\n"
        f"<INVOICES>"
    )
    footer = "</INVOICES>\n" "</DOCUMENT>"

    invoice_xmls = [invoice.to_xml() for invoice in invoices]

    # log the written receipt
    with open(f"{INVOICES_DIR}/written.csv", "a") as logFile:
        logFile.writelines(
            [
                ",".join(
                    [
                        invoice.invc_sid,
                        str(invoice.invc_no),
                        invoice.comments[0]["comments"],
                        invoice.comments[1]["comments"],
                    ]
                )
                + "\n"
                for invoice in invoices
            ]
        )
    # write invoice to server
    path = r"E:\ECM\Polling\001001A\PROC\IN\Invoice001.xml"
    with open(path, "w") as file:
        file.write(
            header
            + "".join([s.replace('<?xml version="1.0" ?>', "") for s in invoice_xmls])
            + footer
        )
    # proc in receipt
    os.system("E:\\ECM\\ecmproc -a -in -stid:001001A")


def write_returns_to_ecm(all_new_returns):
    written_receipts = pd.read_csv(f"{INVOICES_DIR}/written.csv")
    written_receipt_ids = written_receipts.comment1.apply(
        lambda x: x.split(" ")[1]
    ).tolist()
    write_orders_to_ecm(
        [ret for ret in all_new_returns if str(ret.get("id")) in written_receipt_ids],
        # meaning the receipt is of type `return`
        regular=False,
    )
