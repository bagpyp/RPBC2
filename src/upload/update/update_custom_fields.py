from src.api.products import update_custom_field
from src.constants import bc_category_id_to_ebay_category_id


def update_custom_fields(update_id, update_payload):
    # risky accessor :/
    bc_category = str(update_payload["categories"][0])
    ebay_category = bc_category_id_to_ebay_category_id.get(bc_category, "0")
    if update_payload["cf_ebay_category"] != ebay_category:
        update_custom_field(
            update_id,
            "eBay Category ID",
            bc_category_id_to_ebay_category_id.get(bc_category, "0"),
        )

    if update_payload["amazon_price"] != update_payload["cf_ebay_price"]:
        update_custom_field(
            update_id, "eBay Sale Price", update_payload["amazon_price"]
        )
    if update_payload["list_on_amazon"] != update_payload["cf_amazon_status"]:
        if update_payload["list_on_amazon"]:
            update_custom_field(update_id, "Amazon Status", "Enabled")
        else:
            update_custom_field(update_id, "Amazon Status", "Disabled")
