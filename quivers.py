import datetime as dt
import os

import pandas as pd
import paramiko

from secret_info import qftp
from util.path_utils import DATA_DIR

brands = [
    "Marker USA",
    "Dalbello",
    "Tecnica",
    "Blizzard",
    "HEAD SNOWBOARD",
    "Head / Tyrollia",
    "Nordica",
    "Sidas",
]


def send_to_quivers():
    df = pd.read_pickle(f"{DATA_DIR}/ready.pkl").set_index("sku")

    qdf = df.loc[
        # 1- or 2- type product, not class representatives, non-null upc
        df.BRAND.isin(brands) & df.index.str[0].isin(["1", "2"]) & df.UPC.notna(),
        ["name", "UPC", "qty", "pSale"],
    ]

    qdf.columns = ["Product Name", "UPC", "Stock Quantity", "Price"]

    fname = f"Q {str(dt.datetime.now()).split('.')[0].replace(':', '-')}.csv"

    qdf.to_csv(fname, index=False)

    host = qftp["address"]
    port = 22
    password = qftp["password"]
    username = qftp["username"]

    with paramiko.Transport((host, port)) as transport:
        transport.connect(username=username, password=password)
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            sftp.put(fname, fname)

    os.remove(fname)


if __name__ == "__main__":
    print("sending to quivers...")
    send_to_quivers()
    print("sent.")
