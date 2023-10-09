from src.data_maps import customer_data


def customer_attrib(order):
    customer_attrib = dict(
        shipping="0",
        cust_sid=customer_data[order["payment_zone"]]["sid"],
        cust_id=customer_data[order["payment_zone"]]["id"],
        store_no="1",
        station="0",
        first_name=order["payment_zone"],
        last_name=order["payment_zone"],
        detax="0",
        # TODO ask ken, modified_date?
        sbs_no="1",
        cms="1",
        country_name="UNITED_STATES",
    )
    return customer_attrib
