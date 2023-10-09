def base_items(order, ecm_data):
    base_items = []
    for product in order["products"]:
        sku = product["sku"].split("-")[1].lstrip("0")
        try:
            record = (
                ecm_data.fillna("").astype(str)[ecm_data.sku == sku].iloc[0].to_dict()
            )
        except IndexError:
            continue
        base_item = {
            "item_sid": str(record["isid"]),
            "upc": str(record["UPC"]),
            "alu": str(record["sku"]),
            "style_sid": str(record["ssid"]),
            "dcs_code": record["DCS"],
            "vend_code": record["VC"],
            "description1": record["name"],
            "description2": record["year"],
            "description3": record["alt_color"],
            "description4": record["mpn"],
            "attr": record["color"],
            "siz": record["size"],
            "cost": record["cost"],
            "flag": "0",  # was told this was important
        }
        base_items.append(base_item)
    return base_items
