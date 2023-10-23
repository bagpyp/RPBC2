import requests

from config import headers, base


def get_product_id_by_sku(sku):
    h = headers.copy()
    url = base + f"v3/catalog/products?sku={sku}&include_fields=id"
    res = requests.get(url, headers=h)
    data = res.json()["data"]
    return [d["id"] for d in data]
