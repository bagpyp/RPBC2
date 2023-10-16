import time
from xml.dom import minidom as md
from xml.etree import ElementTree as ET

import pandas as pd

from src.util.path_utils import DATA_DIR
from .base_items import base_items
from .comments import comments
from .customer_attrib import customer_attrib
from .fee_attrib import fee_attrib
from .invc_items import invc_items
from .invoice_attrib import invoice_attrib
from .tender_attrib import tender_attrib


def _sid():
    sid = str(int(hash(str(time.time())) % 1e13))
    time.sleep(0.1)
    return sid


class Invoice:
    def __init__(self, order, no, regular=True):
        self.ecm_data = pd.read_pickle(f"{DATA_DIR}/fromECM.pkl")
        c = comments(order)
        self.invc_sid = _sid()
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
                *(invc_items(order, self.ecm_data), base_items(order, self.ecm_data))
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
