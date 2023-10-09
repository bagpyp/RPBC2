import pandas as pd
from numpy import where
from tqdm import tqdm

from src.api import update_custom_field, get_all_brand_ids
from src.util.path_utils import DATA_DIR

#  copied list from main.py, can't import it without running main
amazon_excluded_vendors = [
    "686",
    "Arbor Snowboards",
    "Arcade Belts",
    "Bronson Speed Co.",
    "Bullet",
    "Burton",
    "Capita",
    "Crab Grab",
    "Creature",
    "Darn Tough",
    "Gnu",
    "Havaianas",
    "Helly Hansen",
    "Hestra",
    "Hot Chillys",
    "Hydro Flask",
    "Independent",
    "Lib Technologies",
    "Marmot",
    "Nike",
    "OJ Iii",
    "PIT VIPER",
    "Picture Organic Clothing",
    "RVCA",
    "Reef",
    "Ricta",
    "Salomon Ski",
    "Santa Cruz",
    "Smartwool",
    "Smith",
    "Spyder Active Sports",
    "Stance",
    "Sun Bum",
    "The North Face",
    "Theragun",
    "Turtle Fur",
    "Under Armour",
    "Union Binding Company",
    "Vans",
    "Wolfgang",
]  # ex/ "686",
big_commerce_brands = get_all_brand_ids()
big_commerce_brands = {
    v: k for k, v in big_commerce_brands.items()
}  # ex/ "187 Killer Pads": 5856,

#  unique brand IDs in BC of brands we can't list on Amazon
amazon_excluded_brand_ids = list(
    set([big_commerce_brands.get(vendor, None) for vendor in amazon_excluded_vendors])
)
if None in amazon_excluded_brand_ids:
    amazon_excluded_brand_ids.remove(None)

pdf = pd.read_pickle(f"{DATA_DIR}/products.pkl")
cols = ["p_brand_id", "p_id"]
pdf = pdf[cols].copy()
pdf.loc[:, "p_brand_id"] = pdf["p_brand_id"].astype(int)
pdf["amazon_status"] = where(
    pdf.p_brand_id.isin(amazon_excluded_brand_ids), "Disabled", "Enabled"
)
pdf.drop_duplicates("p_id", inplace=True)
pdf.loc[:, "p_id"] = pdf.p_id.astype(int)

custom_fields = pdf.set_index("p_id").amazon_status.to_dict()

if __name__ == "__main__":
    print("Flooding products in BigCommerce with Amazon Status custom field...")
    pdf = pd.read_pickle(f"{DATA_DIR}/products.pkl")
    pdf_changed = False
    for p_id, amazon_status in tqdm(custom_fields.items()):
        res = update_custom_field(p_id, "Amazon Status", amazon_status)
        if not res.ok:
            if "A product was not found with an id of " in res.text:
                print(f"Removing product with id {p_id} from `products.pkl`")
                pdf = pdf[pdf.p_id != p_id]
                pdf_changed = True
    if pdf_changed:
        print("Committing pdf changes to products.pkl")
        pdf.to_pickle(f"{DATA_DIR}/products.pkl")
