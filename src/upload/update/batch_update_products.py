from math import ceil

from src.api.products import update_products


def batch_update_products(data):
    batches = ceil(len(data) / 10)
    print(f"Updating {batches} product batches in BigCommerce...")
    for i in range(batches):
        update_products(data[int(10 * i) : int(10 * (i + 1))])
