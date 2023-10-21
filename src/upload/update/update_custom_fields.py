from src.api.products import update_custom_field


def update_custom_fields(update_id, update_payload):
    if update_payload["amazon_price"] != update_payload["cf_ebay_price"]:
        update_custom_field(
            update_id, "eBay Sale Price", update_payload["amazon_price"]
        )
    if update_payload["list_on_amazon"] != update_payload["cf_amazon_status"]:
        if update_payload["list_on_amazon"]:
            update_custom_field(update_id, "Amazon Status", "Enabled")
        else:
            update_custom_field(update_id, "Amazon Status", "Disabled")
