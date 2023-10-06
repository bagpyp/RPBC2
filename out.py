import os
import time
import xml.etree.ElementTree as ET
from glob import glob

import pandas as pd
import tqdm
from numpy import nan

from secret_info import stid, drive
from util.path_utils import DATA_DIR


# ecm out


def fromECM(run=True, ecm=True, drive=drive, stid=stid):
    if ecm:
        # procout
        os.system(f"{drive}:\\ECM\\ecmproc -out -a -stid:{stid}")
    # parse inventory cml files and build a list of 'items'
    if run:
        invns = []
        for file in glob(rf"{drive}:\ECM\Polling\{stid}\OUT\Inventory*"):
            invns.extend(ET.parse(file).getroot().findall("./INVENTORYS/INVENTORY"))
            print(f"{file} parsed")

        # turn each item into a dicitonary
        inventorys = []
        print("converting XMLs to DataFrame...")
        time.sleep(1)
        for invn in tqdm.tqdm(invns):
            inventory = {}
            for i in invn:
                inventory.update(i.attrib)
                for j in i:
                    inventory.update(j.attrib)
                    # price, qty and udf uniquesness of keys
                    saw_store = False
                    for n, k in enumerate(j):
                        for x, y in k.attrib.items():
                            if x == "store_no" and y == "1":
                                saw_store = True
                            if x not in ["udf_no", "price_lvl", "store_no"]:
                                inventory.update({x + f"_{n + 1}": y})
                        if not saw_store:
                            inventory.update({"qty_2": "0"})
            # only actuve product
            if inventory["active"] == "1":
                inventorys.append(inventory)

        # drop columns with less than 500 non-null values
        df = pd.DataFrame(inventorys).replace("", nan).dropna(axis=1, how="all")
        df = df[df.active == "1"].reset_index()

        # drop uninteresting columns
        # for col in df:
        #     if df[col].nunique() == 1:
        #         df.drop(col, inplace=True, axis=1)

        # vendors extracted as dictionary
        v_names = {
            v.attrib["vend_code"]: v.attrib["vend_name"]
            for v in ET.parse(rf"{drive}:\ECM\Polling\{stid}\OUT\Vendor.xml")
            .getroot()
            .findall("VENDORS/VENDOR")
        }
        df["brand"] = df["vend_code"].map(v_names)

        # DCSes (or categories) a df itself
        cats = (
            pd.DataFrame(
                [
                    cat.attrib
                    for cat in ET.parse(rf"{drive}:\ECM\Polling\{stid}\OUT\DCS.xml")
                    .getroot()
                    .findall("DCSS/DCS")
                ]
            )
            .replace("", nan)
            .dropna(how="all", axis=1)[["dcs_code", "d_name", "c_name", "s_name"]]
            .dropna(thresh=2)
        )

        # strip, sep with `/` and title() DCSes
        # cats['cat'] = cats.fillna('').iloc[:,1:].apply(\
        #         lambda x: '/'.join(x.str.strip().str.title()),axis=1\
        #     ).str.strip('/')
        cats = cats.fillna("")
        cats["cat"] = (
            cats.d_name.str.strip().str.title()
            + "/"
            + cats.c_name.str.strip().str.title()
            + "/"
            + cats.s_name.str.strip().str.title()
        ).str.strip("/")

        # mergo on `dcs_code`
        df = df.merge(cats, on="dcs_code")

        # naming map for df
        names = {
            "style_sid": "ssid",
            "item_sid": "isid",
            "alu": "sku",
            "upc": "UPC2",
            "local_upc": "UPC",
            "cat": "CAT",
            "brand": "BRAND",
            "description1": "name",
            "description2": "year",
            "description4": "mpn",
            "description3": "alt_color",
            "siz": "size",
            "attr": "color",
            "cost": "cost",
            "price_1": "pSale",
            "price_2": "pMAP",
            "price_3": "pMSRP",
            "price_4": "pAmazon",
            "price_5": "pSWAP",
            "created_date": "fCreated",
            "modified_date": "lModified",
            "fst_rcvd_date": "fRcvd",
            "lst_rcvd_date": "lRcvd",
            "lst_sold_date": "lSold",
            "qty_1": "qty0",
            "qty_2": "qty1",
            "qty_3": "qty",
            "sold_qty_1": "sQty0",
            "sold_qty_2": "sQty1",
            "sold_qty_3": "sQty",
            "dcs_code": "DCS",
            "vend_code": "VC",
            "d_name": "D",
            "c_name": "C",
            "s_name": "S",
            "long_description": "description",
        }

        df = df.rename(columns=names)[names.values()]
        df.to_pickle(f"{DATA_DIR}/fromECM.pkl")
        return df
    if not run:
        return pd.read_pickle(f"{DATA_DIR}/fromECM.pkl")
