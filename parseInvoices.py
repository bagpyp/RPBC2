# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 11:53:48 2020

@author: Web
"""
test = False

import datetime as dt

A = dt.datetime.now()

# prod
from secret_info import drive

import os

if not test:
    print(f"firing up ecm B (18min) at {A.time()}")
    os.system(f"{drive}:\\ECM\\ecmproc -out -a -stid:001001B")
    print("to proc :", dt.datetime.now() - A)

path = f"{drive}:\\ECM\\Polling\\001001B\\OUT"
from glob import glob
import xml.etree.ElementTree as ET

import pandas as pd

pd.options.display.max_rows = 150
pd.options.display.max_columns = 75
pd.options.display.width = 180
pd.options.display.max_colwidth = 30
from collections import Counter
from tqdm import tqdm
from time import sleep

# %%
a = dt.datetime.now()
print("parsing...")


def store(root):
    tree = {}

    def store_tree(root):
        for rpt in [l for l, n in Counter([elt.tag for elt in root]).items() if n > 1]:
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

print("to parse: ", dt.datetime.now() - a)

# %%
import datetime as dt

a = dt.datetime.now()
print("filtering...")

data = [
    {
        k: v
        for k, v in invoice.items()
        if any(
            [s in k for s in ["INVOICE.", "CUSTOMER.", "INVC_COMMENT", "INVC_TENDER."]]
        )
    }
    for invoice in invoices
    if invoice["INVOICE.invc_type"] in list("02")
]

print("to filter: ", dt.datetime.now() - a)

# %%
a = dt.datetime.now()
print("building dataframe...")

df = pd.DataFrame(data)

print("to df: ", dt.datetime.now() - a)

# %% playtime

cols = [
    # 'CUSTOMER.address1',
    # 'CUSTOMER.address2',
    # 'CUSTOMER.address3',
    "CUSTOMER.cms",
    # 'CUSTOMER.company_name',
    "CUSTOMER.country_name",
    "CUSTOMER.cust_id",
    "CUSTOMER.cust_sid",
    "CUSTOMER.detax",
    "CUSTOMER.first_name",
    # 'CUSTOMER.info1',
    # 'CUSTOMER.info2',
    "CUSTOMER.last_name",
    "CUSTOMER.modified_date",
    # 'CUSTOMER.phone1',
    # 'CUSTOMER.phone2',
    "CUSTOMER.sbs_no",
    "CUSTOMER.shipping",
    # 'CUSTOMER.station',
    "CUSTOMER.store_no",
    # 'CUSTOMER.tax_area_name',
    # 'CUSTOMER.zip',
    "INVC_COMMENT-0.comment_no",
    "INVC_COMMENT-0.comments",
    "INVC_COMMENT-1.comment_no",
    "INVC_COMMENT-1.comments",
    "INVC_COMMENT.comment_no",
    "INVC_COMMENT.comments",
    "INVC_TENDER.amt",
    # 'INVC_TENDER.auth',
    "INVC_TENDER.avs_code",
    # 'INVC_TENDER.balance_remaining',
    # 'INVC_TENDER.base_taken',
    # 'INVC_TENDER.cardholder_name',
    # 'INVC_TENDER.cashback_amt',
    # 'INVC_TENDER.cayan_sf_id',
    # 'INVC_TENDER.cayan_trans_key',
    "INVC_TENDER.cent_commit_txn",
    # 'INVC_TENDER.charge_disc_days',
    # 'INVC_TENDER.charge_disc_perc',
    # 'INVC_TENDER.charge_net_days',
    "INVC_TENDER.chk_type",
    # 'INVC_TENDER.crd_exp_month',
    # 'INVC_TENDER.crd_exp_year',
    # 'INVC_TENDER.crd_name',
    "INVC_TENDER.crd_normal_sale",
    "INVC_TENDER.crd_present",
    # 'INVC_TENDER.crd_proc_fee',
    "INVC_TENDER.currency_name",
    # 'INVC_TENDER.doc_no',
    # 'INVC_TENDER.eftdata1',
    # 'INVC_TENDER.emv_aid',
    # 'INVC_TENDER.emv_applabel',
    # 'INVC_TENDER.emv_cryptogram',
    # 'INVC_TENDER.emv_cyrpto_type',
    # 'INVC_TENDER.emv_pin_statement',
    # 'INVC_TENDER.gft_crd_balance',
    # 'INVC_TENDER.gft_crd_int_ref_no',
    "INVC_TENDER.given",
    "INVC_TENDER.matched",
    "INVC_TENDER.orig_currency_name",
    # 'INVC_TENDER.reference',
    # 'INVC_TENDER.take_rate',
    "INVC_TENDER.taken",
    "INVC_TENDER.tender_no",
    "INVC_TENDER.tender_state",
    "INVC_TENDER.tender_type",
    # 'INVC_TENDER.transaction_id',
    # 'INVOICE.activity_perc',
    # 'INVOICE.addr_no',
    # 'INVOICE.audited',
    "INVOICE.clerk_name",
    "INVOICE.clerk_sbs_no",
    "INVOICE.cms_post_date",
    "INVOICE.controller",
    "INVOICE.created_date",
    "INVOICE.createdby_empl_name",
    "INVOICE.createdby_sbs_no",
    "INVOICE.cust_sid",
    "INVOICE.detax",
    "INVOICE.disc_amt",
    "INVOICE.disc_perc",
    "INVOICE.drawer_no",
    "INVOICE.eft_invc_no",
    "INVOICE.elapsed_time",
    "INVOICE.empl_name",
    "INVOICE.empl_sbs_no",
    "INVOICE.held",
    "INVOICE.hisec_type",
    "INVOICE.invc_no",
    "INVOICE.invc_sid",
    "INVOICE.invc_type",
    "INVOICE.modified_date",
    "INVOICE.modifiedby_empl_name",
    "INVOICE.modifiedby_sbs_no",
    # 'INVOICE.note',
    "INVOICE.orig_controller",
    # 'INVOICE.orig_station',
    "INVOICE.orig_store_no",
    # 'INVOICE.over_tax_perc',
    "INVOICE.post_date",
    "INVOICE.proc_status",
    # 'INVOICE.ref_invc_created_date',
    # 'INVOICE.ref_invc_no',
    # 'INVOICE.ref_invc_sid',
    "INVOICE.rounding_offset",
    "INVOICE.sbs_no",
    # 'INVOICE.shipto_addr_no',
    # 'INVOICE.shipto_cust_sid',
    # 'INVOICE.so_no',
    # 'INVOICE.so_sid',
    "INVOICE.station",
    "INVOICE.status",
    "INVOICE.store_no",
    "INVOICE.tax_reb_amt",
    "INVOICE.tax_reb_perc",
    "INVOICE.tracking_no",
    # 'INVOICE.trans_disc_amt',
    "INVOICE.use_vat",
    "INVOICE.vat_options",
    "INVOICE.workstation",
    "INVOICE.ws_seq_no",
    # 'SHIPTO_CUSTOMER.address1',
    # 'SHIPTO_CUSTOMER.address2',
    # 'SHIPTO_CUSTOMER.address3',
    # 'SHIPTO_CUSTOMER.cms',
    # 'SHIPTO_CUSTOMER.company_name',
    # 'SHIPTO_CUSTOMER.country_name',
    "SHIPTO_CUSTOMER.cust_id",
    # 'SHIPTO_CUSTOMER.cust_sid',
    # 'SHIPTO_CUSTOMER.detax',
    "SHIPTO_CUSTOMER.first_name",
    # 'SHIPTO_CUSTOMER.info1',
    # 'SHIPTO_CUSTOMER.info2',
    "SHIPTO_CUSTOMER.last_name",
    # 'SHIPTO_CUSTOMER.modified_date',
    # 'SHIPTO_CUSTOMER.phone1',
    # 'SHIPTO_CUSTOMER.phone2',
    # 'SHIPTO_CUSTOMER.sbs_no',
    # 'SHIPTO_CUSTOMER.shipping',
    # 'SHIPTO_CUSTOMER.station',
    # 'SHIPTO_CUSTOMER.store_no',
    # 'SHIPTO_CUSTOMER.tax_area_name',
    # 'SHIPTO_CUSTOMER.zip'
]

df.to_pickle("accounting/rec.pkl")

# df = df[cols]

# if __name__ == '__main__':

#     for col in df.filter(like='date').columns:
#         df.loc[:,col] = df[col].apply(pd.to_datetime,errors='coerce', utc=True)\
#             .dt.strftime('%Y-%m-%d %H:%M:%S')

#     df['INVOICE.invc_no'] = df['INVOICE.invc_no'].astype(int)

#     masks = [
#         (df['INVOICE.invc_no']>12000)&(df['INVOICE.invc_no']<14000),
#         df['CUSTOMER.last_name'].isin([
#             'BigCommerce',
#             'Big Commerce',
#             'SidelineSwap',
#             ]),
#         df['INVOICE.empl_name']=='web',
#         df['INVC_COMMENT.comments'].str.contains(
#                 'BC|SLS|EBAY|GOOG'
#             )
#     ]
#     df = df[reduce(or_,masks)\
#             & (df['INVOICE.created_date']>'2020-03')\
#             & (df['INVOICE.created_date']<'2021-01')
#             & (df['CUSTOMER.last_name']!='Amazon')]
#     df = df.sort_values(by='INVOICE.created_date')

#     df.to_excel('web_receipts.xlsx')

#     print('to run: ',dt.datetime.now()-A)
