from .pull_orders_from_big_commerce import pull_orders_from_big_commerce
from .pull_orders_from_sideline_swap import pull_orders_from_sideline_swap


def get_all_orders(sideline_swap_is_on):
    if sideline_swap_is_on:
        return sorted(
            pull_orders_from_sideline_swap() + pull_orders_from_big_commerce(),
            key=lambda k: k["created_date"],
        )
    else:
        return sorted(
            pull_orders_from_big_commerce(),
            key=lambda k: k["created_date"],
        )
