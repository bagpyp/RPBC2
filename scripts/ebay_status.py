import pandas as pd
from numpy import where
from tqdm import tqdm

from src.api.products import update_custom_field
from src.util import DATA_DIR

df = pd.read_pickle(f"{DATA_DIR}/ready.pkl")
df = df[df.listOnAmazon]
cols = ["webName", "p_id", "qty", "pAmazon", "listOnAmazon"]
df = df[cols].copy()


def agg(g):
    if len(g) == 1:
        g.pAmazon = g.pAmazon * g.qty
        return g
    else:
        fr = g.iloc[[0], :]
        rog = g.iloc[1:, :]
        fr.pAmazon = (rog.qty * rog.pAmazon).sum()
        return fr


df = df.groupby("webName").apply(agg)
# >>> [(i, df[df.qty >= i].pAmazon.sum()) for i in range(10)]
# [(0, 2070670.08),
# (1, 2070670.08),
# (2, 1892477.96),
# (3, 1679218.97),
# (4, 1457921.33),
# (5, 1302176.78),
# (6, 1142520.08),
# (7, 996432.78),  * first number that sets inventory total below $1M, 7 will be the min
# (8, 891175.2999999999),
# (9, 806191.6599999999)]
ebay_qty_threshold_minimum = 0
while df[df.listOnAmazon & (df.qty >= ebay_qty_threshold_minimum)].pAmazon.sum() > 1_000_000:
    ebay_qty_threshold_minimum += 1

df["ebay_status"] = where(df.qty >= ebay_qty_threshold_minimum, "Enabled", "Disabled")

df.drop_duplicates("p_id", inplace=True)
df.loc[:, "p_id"] = df.p_id.astype(int)

custom_fields = df.set_index("p_id").ebay_status.to_dict()


if __name__ == "__main__":
    print(f"Setting ebay_qty_threshold_minimum to {ebay_qty_threshold_minimum}")
    print("Flooding products in BigCommerce with eBay Status custom field...")
    for p_id, ebay_status in tqdm(custom_fields.items()):
        res = update_custom_field(p_id, "eBay Status", ebay_status)
