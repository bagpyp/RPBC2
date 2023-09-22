# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 12:59:30 2021

@author: Web
"""

from glob import glob
import xml.etree.ElementTree as ET

import pandas as pd
from collections import Counter
from tqdm import tqdm
from time import sleep
import os
import requests
import json
from secret_info import base, drive, headers, sls_base, sls_headers
import datetime as dt


def get_orders(i):
    url = base + f"v2/orders?limit=50&page={i}"
    res = requests.get(url, headers=headers)
    return res


def all_orders():
    orders = []
    n = 1
    while get_orders(i=n).text:
        nthOrders = get_orders(i=n).json()
        orders.extend(nthOrders)
        n += 1
    return orders


def bc():
    print("pulling new orders from BigCommerce...")

    new_orders = all_orders()
    orders = []
    for no in new_orders:
        order = {}
        # ADD CHANNELS HERE
        if no["external_source"].lower() == "google action":
            order["id"] = str(no["id"])
            # TODO change after paments set up in google
            order["payment_id"] = str(no["external_id"])
            order["channel"] = "GOOGLE"
            # TODO change after paments set up in google
            order["payment_zone"] = "GoogleShopping"
        elif no["external_source"].lower() == "facebook":
            order["id"] = str(no["id"])
            order["payment_id"] = str(no["external_id"])
            order["channel"] = "FACEBOOK"
            order["payment_zone"] = "FacebookMarketplace"
        elif no["external_source"].lower() == "ebay":
            order["id"] = no["id"]
            order["payment_id"] = str(no["ebay_order_id"])
            order["channel"] = "EBAY"
            order["payment_zone"] = "Ebay"
        else:
            order["id"] = no["id"]
            order["payment_id"] = no["payment_provider_id"]
            order["channel"] = "BIGCOMMERCE"
            if "authorize.net" in no["payment_method"].lower():
                order["payment_zone"] = "Authorize.Net"
            elif no["payment_method"].lower() == "paypal":
                order["payment_zone"] = "PayPal"
            else:
                order["payment_zone"] = "BigCommerce"
        order["created_date"] = dt.datetime.strptime(
            " ".join(no["date_created"].split(" ")[:-1]), "%a, %d %b %Y %H:%M:%S"
        ).strftime("%Y-%m-%dT%H:%M:%S")
        order["num_items"] = len(no["products"])
        order["total_amt"] = round(float(no["total_inc_tax"]), 2)
        order["status"] = no["status"]
        orders.append(order)
    return orders


def sls():
    print("Checking SidelineSwap...")

    def sls_orders():
        i = 1
        url = sls_base + "orders"
        res = requests.get(url, headers=sls_headers).json()
        data = res["data"]
        while res["meta"]["has_next"]:
            i += 1
            res = requests.get(url + f"?page={i}", headers=sls_headers)
            res = res.json()
            data.extend(res["data"])
        return data

    new_orders = sls_orders()
    orders = []
    for no in new_orders:
        order = {}
        # VARIABLE -
        order["id"] = str(no["order_id"])
        order["payment_id"] = "external"
        order["channel"] = "SIDELINE"  # associate
        order["payment_zone"] = "SidelineSwap"  # customer.first_name
        # VARIABLE ^
        order["created_date"] = no["created_at"].split(".")[0]
        order["num_items"] = 1
        order["total_amt"] = round(float(no["you_earned"]), 2)
        order["products"] = [
            {
                "sku": no["item_sku"],
                "qty": 1,
                "amt_per": no["you_earned"],
                "amt_total": no["you_earned"],
            }
        ]
        if "shipment" in no:
            if "status" in no["shipment"]:
                order["status"] = no["shipment"]["status"]
            else:
                order["status"] = "NO STATUS"
        else:
            order["status"] = "NO STATUS"
        orders.append(order)
    return orders


def pull_invoices(test=False):
    if not test:
        os.system(f"{drive}:\\ECM\\ecmproc -out -a -stid:001001B")

    path = f"{drive}:\\ECM\\Polling\\001001B\\OUT"

    def store(root):
        tree = {}

        def store_tree(root):
            for rpt in [
                l for l, n in Counter([elt.tag for elt in root]).items() if n > 1
            ]:
                for i, relt in enumerate(root.iter(rpt)):
                    if i > 0:
                        relt.tag += "-" + str(i)
            if root.attrib:
                tree.update(
                    {root.tag + "." + k: v for k, v in root.attrib.items() if v != ""}
                )
            for child in root:
                store_tree(child)
            return tree

        return store_tree(root)

    invoices = []
    sleep(0.1)
    for file in tqdm(glob(path + "\\Invoice*.xml")):
        invcs = ET.parse(file).getroot().findall("INVOICES/INVOICE")
        for invc in invcs:
            invoices.append(store(invc))

    data = [
        {
            k: v
            for k, v in invoice.items()
            if any(
                [
                    s in k
                    for s in ["INVOICE.", "CUSTOMER.", "INVC_COMMENT", "INVC_TENDER."]
                ]
            )
        }
        for invoice in invoices
        if invoice["INVOICE.invc_type"] in list("02")  # the two types of receipts
    ]

    df = pd.DataFrame(data)
    df.to_pickle(f"accounting/receipts.pkl")
    df.to_csv(r"\\SERVER\user Shares\Kathy\All Retail Pro Receipts\All RP Receipts.csv")


def pull_orders():
    orders = sorted(bc() + sls(), key=lambda o: o["created_date"])
    with open("accounting/orders.json", "w") as outfile:
        json.dump(orders, outfile)
