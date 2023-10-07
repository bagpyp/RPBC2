import datetime as dt
import json
import os
import time
import xml.dom.minidom as md
import xml.etree.ElementTree as ET

import pandas as pd

from secret_info import stid, drive
from src.data_maps import prefix_map, assoc_map, customer_data
from util.path_utils import DATA_DIR, INVOICES_DIR


# %%


def sid():
    sid = str(int(hash(str(time.time())) % 1e13))
    time.sleep(0.1)
    return sid


def times(time, regular=True):
    utc = dt.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
    if regular:
        now = utc - dt.timedelta(hours=8)
    else:
        now = utc
    a_second_ago = now - dt.timedelta(seconds=1)
    return {
        "utc": dt.datetime.strftime(utc, "%Y-%m-%dT%H:%M:%S"),
        "now": dt.datetime.strftime(now, "%Y-%m-%dT%H:%M:%S"),
        "a_second_ago": dt.datetime.strftime(a_second_ago, "%Y-%m-%dT%H:%M:%S"),
    }


def invoice_attrib(order, no, invc_sid_top, regular=True):
    diff = abs(
        min(
            0,
            round(
                order["total_amt"] - sum([p["amt_total"] for p in order["products"]]), 2
            ),
        )
    )
    if regular:
        t = times(order["created_date"])
    else:
        t = times(dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), regular=False)
    invoice_attrib = dict(
        # invc_sid = sid(),
        invc_sid=invc_sid_top,
        sbs_no="1",
        invc_no=str(no),
        store_no="1",
        invc_type=("2", "0")[regular],
        # TODO invc_no =
        status="0",
        proc_status="0",
        cust_sid=customer_data[order["payment_zone"]]["sid"],
        addr_no="1",
        workstation="3",
        orig_store_no="1",
        use_vat="0",
        vat_options="0",
        disc_perc=str(round(100 * diff / order["total_amt"], 0)),
        disc_amt=str(diff),
        created_date=t["now"],
        modified_date=t["utc"],
        post_date=t["a_second_ago"],
        audited="0",
        cms_post_date=t["a_second_ago"],
        # TODO ask ken, ws_seq_no???
        held="0",
        controller="1",
        orig_controller="1",
        empl_sbs_no="1",
        empl_name="web",
        createdby_sbs_no="1",
        createdby_empl_name="web",
        # TODO ask ken, elapsed_time???,
        modifiedby_sbs_no="1",
        modifiedby_empl_name="web",
        drawer_no="1",
        activity_percent="100",
        # TODO ask ken, eft_invc_no???
        detax="0",
        clerk_sbs_no="1",
        clerk_name=order["channel"][:8]
        # TODO tracking_no
    )
    return invoice_attrib


def customer_attrib(order):
    customer_attrib = dict(
        shipping="0",
        cust_sid=customer_data[order["payment_zone"]]["sid"],
        cust_id=customer_data[order["payment_zone"]]["id"],
        store_no="1",
        station="0",
        first_name=order["payment_zone"],
        last_name=order["payment_zone"],
        detax="0",
        # TODO ask ken, modified_date?
        sbs_no="1",
        cms="1",
        country_name="UNITED_STATES",
    )
    return customer_attrib


def tender_attrib(order):
    tender_attrib = dict(
        tender_type="4",
        tender_no="1",
        taken=str(order["total_amt"]),
        given="0",
        amt=str(order["total_amt"]),
        tender_state="0",
        orig_currency_name="DOLLARS",
        currency_name="DOLLARS",
        crd_normal_sale="1",
        crd_present="0",
        matched="0",
        avs_code="0",
        chk_type="0",
        cent_commit_txn="0",
    )
    return tender_attrib


def comments(order):
    comments = ["", ""]
    comments[0] = prefix_map[order["channel"]] + " " + str(order["id"])
    if order["payment_id"]:
        comments[1] = str(order["payment_id"])
    return comments


def fee_attrib(order):
    diff = max(
        0,
        round(order["total_amt"] - sum([p["amt_total"] for p in order["products"]]), 2),
    )
    fee_attrib = dict(
        fee_type="9", tax_perc="0", tax_incl="0", amt=str(diff), fee_name="Shipng"
    )
    return fee_attrib


def items(order, ecm_data):
    items = []
    for i, product in enumerate(order["products"]):
        sku = product["sku"].split("-")[1].lstrip("0")
        try:
            record = (
                ecm_data.fillna("").astype(str)[ecm_data.sku == sku].iloc[0].to_dict()
            )
        except IndexError:
            # this would mean that the item with sku "sku" does not exist in Retail Pro
            continue
        item = {
            "item_pos": str(i + 1),
            "item_sid": str(record["isid"]),
            "qty": str(product["qty"]),
            "orig_price": str(record["pSale"]),
            "price": str(product["amt_per"]),
            "kit_flag": "0",
            "price_lvl": "1",
            "orig_tax_amt": "0",
            "tax_amt": "0",
            "empl_name": order["channel"][:8],
            "empl_id": assoc_map[order["channel"]],
        }
        items.append(item)
    return items


def base_items(order, ecm_data):
    base_items = []
    for product in order["products"]:
        sku = product["sku"].split("-")[1].lstrip("0")
        try:
            record = (
                ecm_data.fillna("").astype(str)[ecm_data.sku == sku].iloc[0].to_dict()
            )
        except IndexError:
            continue
        base_item = {
            "item_sid": str(record["isid"]),
            "upc": str(record["UPC"]),
            "alu": str(record["sku"]),
            "style_sid": str(record["ssid"]),
            "dcs_code": record["DCS"],
            "vend_code": record["VC"],
            "description1": record["name"],
            "description2": record["year"],
            "description3": record["alt_color"],
            "description4": record["mpn"],
            "attr": record["color"],
            "siz": record["size"],
            "cost": record["cost"],
            "flag": "0",  # was told this was important
        }
        base_items.append(base_item)
    return base_items


class Invoice:
    def __init__(self, order, no, regular=True):
        self.ecm_data = pd.read_pickle(f"{DATA_DIR}/fromECM.pkl")
        c = comments(order)
        self.invc_sid = sid()
        self.invc_no = no
        self.invoice_attrib = invoice_attrib(order, no, self.invc_sid, regular=regular)
        # self.invoice_attrib.update({'invc_no':f'{no}'})
        self.customer_attrib = customer_attrib(order)
        self.tender_attrib = tender_attrib(order)
        self.fee_attrib = fee_attrib(order)
        self.comments = [
            {"comment_no": "1", "comments": f"{c[0]}"},
            {"comment_no": "2", "comments": f"{c[1]}"},
        ]
        self.invc_items = [
            {"invc_item": i, "invc_base_item": b}
            for i, b in zip(
                *(items(order, self.ecm_data), base_items(order, self.ecm_data))
            )
        ]

    def to_xml(self):
        invoice = ET.Element("INVOICE", self.invoice_attrib)
        ET.SubElement(invoice, "CUSTOMER", self.customer_attrib)
        ET.SubElement(invoice, "SHIPTO_CUSTOMER")
        ET.SubElement(invoice, "INVC_SUPPLS")
        invc_comments = ET.SubElement(invoice, "INVC_COMMENTS")
        ET.SubElement(invc_comments, "INVC_COMMENT", self.comments[0])
        ET.SubElement(invc_comments, "INVC_COMMENT", self.comments[1])
        ET.SubElement(invoice, "INVC_EXTRAS")
        fees = ET.SubElement(invoice, "INVC_FEES")
        ET.SubElement(fees, "INVC_FEE", self.fee_attrib)
        invc_tenders = ET.SubElement(invoice, "INVC_TENDERS")
        ET.SubElement(invc_tenders, "INVC_TENDER", self.tender_attrib)
        invoice_items = ET.SubElement(invoice, "INVC_ITEMS")
        for item in self.invc_items:
            invc_item = ET.SubElement(invoice_items, "INVC_ITEM", item["invc_item"])
            ET.SubElement(invc_item, "INVC_BASE_ITEM", item["invc_base_item"])
        rough_xml = ET.tostring(invoice, "unicode")
        dom = md.parseString(rough_xml)
        return dom.toprettyxml()


def document(orders, ecm=True, drive=drive, stid=f"{stid}", regular=True):
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
            path = rf"{drive}:\ECM\Polling\{stid}\PROC\IN\Invoice001.xml"
            # write invoice to invoices/
            with open(f"{INVOICES_DIR}/Invoice{sid()}.xml", "w") as otherFile:
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
            os.system(f"{drive}:\\ECM\\ecmproc -a -in -stid:{stid}")

        else:
            with open("Invoice001.xml", "w") as file:
                file.write(
                    header
                    + "".join(
                        [s.replace('<?xml version="1.0" ?>', "") for s in invoice_xmls]
                    )
                    + footer
                )
