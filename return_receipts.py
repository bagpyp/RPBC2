test = True

import json
from returns import get_returns
import pandas as pd

pd.options.mode.chained_assignment = None
pd.options.display.max_rows = 150
pd.options.display.max_columns = 75
pd.options.display.width = 170
pd.options.display.max_colwidth = 30

if not test:
    returns = get_returns(test=test)
    # json.dump(returns,outfile)

written = pd.read_csv("invoices/written.csv", dtype={"invc_no": str, "invc_sid": str})
rec = pd.read_pickle("accounting/receipts.pkl")
rec = rec[
    [
        "INVOICE.invc_sid",
        "INVOICE.invc_no",
        "INVOICE.invc_type",
        # 'INVOICE.hisec_type',
        # 'INVOICE.status',
        "INVOICE.proc_status",
        "INVOICE.created_date",
        # 'INVOICE.modified_date',
        # 'INVOICE.post_date',
        # 'INVOICE.held',
        # 'INVOICE.empl_name',
        # 'INVOICE.createdby_empl_name',
        # 'CUSTOMER.first_name',
        "CUSTOMER.last_name",
        "INVC_COMMENT.comments",
        "INVC_COMMENT-1.comments",
        # 'INVC_TENDER.tender_type',
        "INVC_TENDER.amt",
        # 'INVC_TENDER.currency_name',
        # 'INVOICE.clerk_name',
    ]
].rename(
    columns={
        "INVC_COMMENT.comments": "_.comment1",
        "INVC_COMMENT-1.comments": "_.comment2",
    }
)
rec.columns = [_.split(".")[1] for _ in rec.columns]
rec = rec[rec.comment1.str.contains(r"^(FB|BC|SLS|EBAY|GOOGLE).*\d$").fillna(False)]
for c in ["created_date"]:
    rec[c] = pd.to_datetime(rec[c])
rec["order_id"] = rec.comment1.apply(lambda s: s.split(" ")[1]).astype(str)
rec = rec.iloc[-1::-1]
rec.order_id = rec.order_id.astype(str)

# %%
if test:
    with open("accounting/allReturns.json") as file:
        returns = pd.DataFrame(json.load(file)).drop("products", 1).iloc[-1::-1]
        returns = returns[
            ["id", "payment_id", "payment_zone", "created_date", "total_amt"]
        ]
        returns.id = returns.id.astype(str)
    # %%

    a = returns.merge(
        rec[rec.invc_type == "0"],
        left_on="id",
        right_on="order_id",
        how="left",
        suffixes=("_BC", "_RP"),
    ).merge(
        written,
        left_on="invc_sid",
        right_on="invc_sid",
        how="left",
        suffixes=("", "_written"),
    )
    b = returns.merge(
        rec[rec.invc_type == "2"],
        left_on="id",
        right_on="order_id",
        how="left",
        suffixes=("_BC", "_RP"),
    )
    df = pd.concat([a, b], ignore_index=True).sort_values(
        by="created_date_BC", ascending=False
    )
    df = df[df.proc_status.fillna("0").astype(int) < 4]
    # df = df[pd.to_datetime(df.created_date_BC).dt.year==2021]

    df["num_receipts"] = 0
    for i in range(df.groupby("id").invc_sid.count().max() + 1):
        df.loc[
            df.groupby("id").filter(lambda g: g.invc_sid.count() == i).index,
            "num_receipts",
        ] = i

    keystone = df[["id", "invc_type", "proc_status"]]

    # %%
    df.to_csv("forkathy.csv")
