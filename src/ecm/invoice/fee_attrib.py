def fee_attrib(order):
    diff = max(
        0,
        round(order["total_amt"] - sum([p["amt_total"] for p in order["products"]]), 2),
    )
    fee_attrib = dict(
        fee_type="9", tax_perc="0", tax_incl="0", amt=str(diff), fee_name="Shipng"
    )
    return fee_attrib
