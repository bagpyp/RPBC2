import json

from src.api.categories.get_all_category_ids import get_all_category_ids
from src.util import DATA_DIR


def download_category_ids():
    category_ids = get_all_category_ids()
    with open(f"{DATA_DIR}/category_ids.json", "w") as file:
        json.dump(category_ids, file, indent=4)
