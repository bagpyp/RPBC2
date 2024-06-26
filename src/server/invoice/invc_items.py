from src.constants import channel_name_to_employee_id


def invc_items(order, ecm_data):
    invc_items = []
    for i, product in enumerate(order["products"]):
        sku = product["sku"].split("-")[1].lstrip("0")
        try:
            record = (
                ecm_data.fillna("").astype(str)[ecm_data.sku == sku].iloc[0].to_dict()
            )
        except IndexError:
            # this would mean that the item with sku "sku" does not exist in Retail Pro
            continue
        invc_item = {
            "item_pos": str(i + 1),
            "item_sid": str(record["isid"]),
            "qty": str(product["qty"]),
            # TODO: make this 85% of pAmazon for all non-BC orders
            "orig_price": str(record["pSale"]),
            "price": str(product["amt_per"]),
            "kit_flag": "0",
            "price_lvl": "1",
            "orig_tax_amt": "0",
            "tax_amt": "0",
            "empl_name": order["channel"][:8],
            "empl_id": channel_name_to_employee_id[order["channel"]],
            "cost": record["cost"],
        }
        invc_items.append(invc_item)
    return invc_items
