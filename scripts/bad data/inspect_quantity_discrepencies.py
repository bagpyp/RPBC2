import pandas as pd

from src.util import DATA_DIR


def inspect():
    pd.options.display.max_rows = 1000
    pd.options.display.max_columns = 100
    pd.options.display.width = 300

    ready = pd.read_pickle(f"{DATA_DIR}/ready.pkl")

    cols = ["webName", "sku", "qty", "p_qty", "v_qty", "lModified"]
    r = ready[cols]
    r = r.groupby("webName").filter(lambda g: g.p_qty.sum() != 0)
    r.loc[r.sku.str[0].isin(["1", "2"]), "p_qty"] = r.loc[
        r.sku.str[0].isin(["1", "2"]), "v_qty"
    ]
    r.drop("v_qty", axis=1, inplace=True)
    r.p_qty = r.p_qty.astype(int)
    df = r[r.webName.isin(r[r.qty != r.p_qty].webName)]

    products = pd.read_pickle(f"{DATA_DIR}/products.pkl")
    p_cols = ["p_id", "v_id", "p_name", "p_sku", "v_sku", "p_qty", "v_qty"]
    p = products[p_cols]
    p = p[p.p_name.isin(df.webName)]

    # danglers
    rp = df[~(df.sku.isin(p.v_sku) | df.sku.isin(p.p_sku))]
    bc = p[~(p.p_sku.isin(df.sku) | p.v_sku.isin(df.sku))]
    bc = bc.sort_values(by=["p_name", "v_sku"])
    rp = rp.sort_values(by=["webName", "sku"])

    print("debug")


if __name__ == "__main__":
    inspect()
