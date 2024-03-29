from src.download.orders.pull_orders_from_big_commerce import (
    pull_orders_from_big_commerce,
)
from src.download.orders.pull_orders_from_sideline_swap import (
    pull_orders_from_sideline_swap,
)


def get_all_returns(sideline_swap_is_on):
    if sideline_swap_is_on:
        return sorted(
            pull_orders_from_sideline_swap(kind="returns")
            + pull_orders_from_big_commerce(kind="returns"),
            key=lambda k: k["created_date"],
        )
    else:
        return sorted(
            pull_orders_from_big_commerce(kind="returns"),
            key=lambda k: k["created_date"],
        )
