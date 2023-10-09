def tender_attrib(order):
    tender_attrib = dict(
        tender_type="4",
        tender_no="1",
        taken=str(order["total_amt"]),
        given="0",
        amt=str(order["total_amt"]),
        tender_state="0",
        orig_currency_name="DOLLARS",
        currency_name="DOLLARS",
        crd_normal_sale="1",
        crd_present="0",
        matched="0",
        avs_code="0",
        chk_type="0",
        cent_commit_txn="0",
    )
    return tender_attrib
