import json
import os
import time

from src.server.invoice.invoice import Invoice
from src.util.path_utils import DATA_DIR, INVOICES_DIR


def _sid():
    sid = str(int(hash(str(time.time())) % 1e13))
    time.sleep(0.1)
    return sid


def write_orders_to_ecm(orders, ecm=True, regular=True):
    kind = "orders" if regular else "returns"
    order_counts = {}
    for api_source in ["sls", "bc"]:
        with open(f"{DATA_DIR}/{api_source}_orders.json") as f:
            order_counts[api_source] = len(json.load(f))

    return_counts = {}
    for api_source in ["sls", "bc"]:
        with open(f"{DATA_DIR}/{api_source}_returns.json") as f:
            return_counts[api_source] = len(json.load(f))

    if orders:
        print(f"Found {len(orders)} {kind} online")
        header = f'<?xml version="1.0" encoding="UTF-8"?>\n<!-- Created on {time.strftime("%Y-%m-%dT%H:%M:%S")}-08:00 -->\n<!-- V9 STATION -->\n<DOCUMENT>\n<INVOICES>'
        footer = "</INVOICES>\n</DOCUMENT>"
        if regular:
            invoices = [
                Invoice(order, sum(list(order_counts.values())) + i + 1 + 13003)
                for i, order in enumerate(orders)
            ]
        else:
            invoices = [
                Invoice(
                    order,
                    sum(list(return_counts.values())) + i + 1 + 50000,
                    regular=False,
                )
                for i, order in enumerate(orders)
            ]
        invoice_xmls = [invoice.to_xml() for invoice in invoices]
        if ecm:
            path = r"E:\ECM\Polling\001001A\PROC\IN\Invoice001.xml"
            # write invoice to invoice/
            with open(f"{INVOICES_DIR}/Invoice{_sid()}.xml", "w") as otherFile:
                otherFile.write(
                    header
                    + "".join(
                        [s.replace('<?xml version="1.0" ?>', "") for s in invoice_xmls]
                    )
                    + footer
                )
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
            # write invoice to server and procin
            with open(path, "w") as file:
                file.write(
                    header
                    + "".join(
                        [s.replace('<?xml version="1.0" ?>', "") for s in invoice_xmls]
                    )
                    + footer
                )
            os.system("E:\\ECM\\ecmproc -a -in -stid:001001A")

        else:
            with open("Invoice001.xml", "w") as file:
                file.write(
                    header
                    + "".join(
                        [s.replace('<?xml version="1.0" ?>', "") for s in invoice_xmls]
                    )
                    + footer
                )
