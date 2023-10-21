from math import ceil

from src.api.products import update_products


def batch_update_products(data):
    batches = ceil(len(data) / 10)
    for i in range(batches):
        if i + 1 < batches:
            update_products(data[int(10 * i) : int(10 * (i + 1))])
        else:
            update_products(data[int(10 * i) :])
