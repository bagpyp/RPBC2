# prefixes for `comment 1` in Retail Pro receipts
channel_name_to_prefix = {
    "EBAY": "EBAY",
    "GOOGLE": "GOOGLE",
    "SIDELINE": "SLS",
    "BIGCOMMERCE": "BC",
    "AMAZON": "AZ",  # Amazon
    "___": "WSH",
    "____": "RK",
    "WALMART": "WAL",
    "FACEBOOK": "FB",
    "_______": "QUIV",
    "________": "STRON",
}

# employee ids for `associate` field in Retail Pro
# indicates who is responsible for the sale
channel_name_to_employee_id = {
    "EBAY": "122",
    "GOOGLE": "129",
    "SIDELINE": "113",
    "BIGCOMMERCE": "109",
    "AMAZON": "136",  # Amazon
    "___": "WSH",
    "____": "RK",
    "WALMART": "140",
    "FACEBOOK": "134",
    "_______": "QUIV",
    "________": "STRON",
}

# customer charged on receipt (based on payment processor)
payment_zone_name_to_rp_ids = {
    "Authorize.Net": {"sid": "6006417736096747516", "id": "1010176"},
    "PayPal": {"sid": "791550355979724528", "id": "28207"},
    "SidelineSwap": {"sid": "5757614230247772156", "id": "1008618"},
    "GoogleShopping": {"sid": "6006479495503482876", "id": "1010179"},
    # default payment zone
    "BigCommerce": {"sid": "5274779657848317680", "id": "38342"},
    "GooglePay": {"sid": "6043739532885954556", "id": "1010761"},
    "FacebookMarketplace": {"sid": "6421257710870138876", "id": "1013049"},
    "Ebay": {"sid": "-2005425994566899984", "id": "23780"},
    "Amazon": {"sid": "-2532916938669988112", "id": "22845"},
    "Walmart": {"sid": "6502758247952333296", "id": "1013487"},
}
