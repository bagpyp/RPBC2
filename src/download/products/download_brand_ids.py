import json

from src.api import get_all_brand_ids
from src.util import DATA_DIR


def download_brand_ids():
    brands = get_all_brand_ids()
    with open(f"{DATA_DIR}/brand_ids.json", "w") as file:
        json.dump(brands, file, indent=4)
