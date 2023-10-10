from src.constants import prefix_map


def comments(order):
    comments_array = ["", ""]
    comments_array[0] = prefix_map[order["channel"]] + " " + str(order["id"])
    if order["payment_id"]:
        comments_array[1] = str(order["payment_id"])
    return comments_array
