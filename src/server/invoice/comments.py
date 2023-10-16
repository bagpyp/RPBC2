from src.constants import channel_name_to_prefix


def comments(order):
    comments_array = ["", ""]
    comments_array[0] = (
        channel_name_to_prefix[order["channel"]] + " " + str(order["id"])
    )
    if order["payment_id"]:
        comments_array[1] = str(order["payment_id"])
    return comments_array
