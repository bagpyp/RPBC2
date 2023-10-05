import requests

from secret_info import headers, base


def delete_product(id_):
    h = headers.copy()
    url = base + f"v3/catalog/products/{id_}"
    res = requests.delete(url, headers=h)
    return res
