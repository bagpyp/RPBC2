# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:27:43 2020

@author: Web
"""

customer_data = {
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

prefix_map = {
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

# employee data, used for Associate fields
assoc_map = {
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

category_map = {
    "Disc Golf/Bag": "Misc",
    "Electronic/Audio": "Misc",
    "Electronic/Camera/Accessory": "Misc",
    "Eyewear/Goggles/Accessory": "Outerwear/Goggles/Accessory",
    "Eyewear/Goggles/Moto": "Outerwear/Goggles/Accessory",
    "Eyewear/Goggles/Rep. Lens": "Outerwear/Goggles/Accessory",
    "Eyewear/Goggles/Unisex": "Outerwear/Goggles/Adult",
    "Eyewear/Goggles/Womens": "Outerwear/Goggles/Women",
    "Eyewear/Goggles/Youth": "Outerwear/Goggles/Youth",
    "Eyewear/Sunglasses/Accessory": "Lifestyle/Sunglasses/Accessory",
    "Eyewear/Sunglasses/Unisex": "Lifestyle/Sunglasses/Unisex",
    "Eyewear/Sunglasses/Womens": "Lifestyle/Sunglasses/Womens",
    "Headwear/Beanie": "Outerwear/Headwear/Beanie",
    "Headwear/Facemask": "Outerwear/Headwear/Facemask",
    "Headwear/Hat": "Lifestyle/Accessory",
    "Hike/Pack/Accessory": "Lifestyle/Accessory",
    "Hike/Pack/Hydration": "Lifestyle/Accessory",
    "Hike/Pack/Map/Book": "Lifestyle/Accessory",
    "Hike/Pack/Mens/Shoes": "Lifestyle/Men/Shoes",
    "Hike/Pack/Womens/Shoes": "Lifestyle/Women/Shoes",
    "Kayak/Accessory": "Watersport/Kayak",
    "Lifejacket/Neoprene/Dog": "Watersport/Life Jackets/Dog",
    "Lifejacket/Neoprene/Men": "Watersport/Life Jackets/Men",
    "Lifejacket/Neoprene/Womens": "Watersport/Life Jackets/Women",
    "Lifejacket/Neoprene/Youth": "Watersport/Life Jackets/Youth",
    "Lifejacket/Nylon/Men": "Watersport/Life Jackets/Men",
    "Lifejacket/Nylon/Womens": "Watersport/Life Jackets/Women",
    "Lifejacket/Nylon/Youth": "Watersport/Life Jackets/Youth",
    "Mens/Baselayer/Bottom": "Outerwear/Base Layer/Men",
    "Mens/Baselayer/Suit": "Outerwear/Base Layer/Men",
    "Mens/Baselayer/Top": "Outerwear/Base Layer/Men",
    "Mens/Lifestyle/Accessory": "Lifestyle/Men/Accessory",
    "Mens/Lifestyle/Bag": "Lifestyle/Men/Accessory",
    "Mens/Lifestyle/Jacket": "Lifestyle/Men/Jacket",
    "Mens/Lifestyle/Pants": "Lifestyle/Men/Pants",
    "Mens/Lifestyle/Shoes": "Lifestyle/Men/Shoes",
    "Mens/Lifestyle/Shorts": "Lifestyle/Men/Shorts",
    "Mens/Lifestyle/Top": "Lifestyle/Men/Tops",
    "Mens/Midlayer": "Outerwear/Midlayer/Men",
    "Mens/Outerwear/Gloves": "Outerwear/Gloves/Men",
    "Mens/Outerwear/Jackets": "Outerwear/Jacket/Men",
    "Mens/Outerwear/Mittens": "Outerwear/Mittens/Men",
    "Mens/Outerwear/Pants": "Outerwear/Pants/Men",
    "Mens/Outerwear/Suit": "Outerwear/Suit",
    "Mens/Swimwear/Shorts": "Lifestyle/Men/Shorts",
    "Race/Night": "Misc",
    "Safety/Avalanche/Probe": "Misc",
    "Safety/Avalanche/Shovel": "Misc",
    "Safety/Avalanche/Tranceiver": "Misc",
    "Safety/Helmet/Skate": "Skate/Helmets",
    "Safety/Helmet/Ski": "Ski/Helmets",
    "Safety/Helmet/Wakeboard": "Watersport/Wakeboard/Accessory",
    "Safety/Pad/Skate": "Skate/Accessory",
    "Safety/Pad/Snow": "Snowboard/Accessory",
    "Safety/Race/Ski": "Ski/Accessory",
    "Skateboard/Accessory": "Skate/Accessory",
    "Skateboard/Bearings": "Skate/Bearings",
    "Skateboard/Complete/Street": "Skate/Completes",
    "Skateboard/Completes/Long Board": "Skate/Completes",
    "Skateboard/Deck/Street": "Skate/Decks",
    "Skateboard/Griptape": "Skate/Accessory",
    "Skateboard/Hardware": "Skate/Accessory",
    "Skateboard/Shoes/Mens": "Skate/Shoes/Men",
    "Skateboard/Shoes/Womens": "Skate/Shoes/Women",
    "Skateboard/Trucks/Street": "Skate/Trucks",
    "Skateboard/Wheels/Longboard": "Skate/Wheels",
    "Skateboard/Wheels/Street": "Skate/Wheels",
    "Ski/Accessory": "Ski/Accessory",
    "Ski/Accessory/Insoles": "Ski/Accessory",
    "Ski/Bags/Backpack": "Ski/Accessory",
    "Ski/Bags/Boot": "Ski/Accessory",
    "Ski/Bags/Outerwear/": "Ski/Accessory",
    "Ski/Bags/Ski": "Ski/Accessory",
    "Ski/Bindings/Mens": "Ski/Bindings/Men",
    "Ski/Bindings/Womens": "Ski/Bindings/Women",
    "Ski/Bindings/Youth": "Ski/Bindings/Youth",
    "Ski/Boots/Accessory": "Ski/Accessory",
    "Ski/Boots/Liner": "Ski/Accessory",
    "Ski/Boots/Mens": "Ski/Boots/Men",
    "Ski/Boots/Parts": "Ski/Boots/Parts",
    "Ski/Boots/Womens": "Ski/Boots/Women",
    "Ski/Boots/Youth": "Ski/Boots/Youth",
    "Ski/Poles/Accessory": "Ski/Accessory",
    "Ski/Poles/Adult": "Ski/Poles/Adult",
    "Ski/Poles/Baskets": "Ski/Accessory",
    "Ski/Poles/Youth": "Ski/Poles/Youth",
    "Ski/Skis/Mens": "Ski/Skis/Men",
    "Ski/Skis/Womens": "Ski/Skis/Women",
    "Ski/Skis/Youth": "Ski/Skis/Youth",
    "Ski/Socks/Adult": "Ski/Socks/Adult",
    "Ski/Socks/Youth": "Ski/Socks/Youth",
    "Ski/Tune/Wax": "Ski/Accessory",
    "Ski/Tuning/Tool": "Ski/Accessory",
    "Ski/X-Country/Bindings": "Ski/Accessory",
    "Ski/X-Country/Boots": "Ski/Accessory",
    "Ski/X-Country/Skis": "Ski/Accessory",
    "Snowboard/Accessory": "Snowboard/Accessory",
    "Snowboard/Bags/Backpack": "Snowboard/Bags/Backpack",
    "Snowboard/Bags/Board Bag": "Snowboard/Bags/Board",
    "Snowboard/Bags/Outerwear/": "Snowboard/Bags/Outerwear/",
    "Snowboard/Bags/Travel": "Snowboard/Bags/Travel",
    "Snowboard/Bags/Wheel": "Snowboard/Bags/Wheel",
    "Snowboard/Bindings/Unisex": "Snowboard/Bindings/Adult",
    "Snowboard/Bindings/Women": "Snowboard/Bindings/Women",
    "Snowboard/Bindings/Youth": "Snowboard/Bindings/Youth",
    "Snowboard/Board/Mens": "Snowboard/Board/Men",
    "Snowboard/Board/Womens": "Snowboard/Board/Women",
    "Snowboard/Board/Youth": "Snowboard/Board/Youth",
    "Snowboard/Boots/Mens": "Snowboard/Boots/Men",
    "Snowboard/Boots/Womens": "Snowboard/Boots/Women",
    "Snowboard/Boots/Youth": "Snowboard/Boots/Youth",
    "Snowboard/Socks/Adult": "Snowboard/Accessory",
    "Snowboard/Socks/Youth": "Snowboard/Accessory",
    "Stupid/Misc/Crap": "Misc",
    "Wakeboard/Accessory": "Watersport/Wakeboard/Accessory",
    "Wakeboard/Bags": "Watersport/Wakeboard/Accessory",
    "Wakeboard/Board/Mens": "Watersport/Wakeboard/Board",
    "Wakeboard/Boots/Unisex": "Watersport/Wakeboard/Accessory",
    "Wakeboard/Boots/Womens": "Watersport/Wakeboard/Accessory",
    "Wakeboard/Packages/Unisex": "Watersport/Wakeboard/Package Deals",
    "Wakeboard/Packages/Womens": "Watersport/Wakeboard/Package Deals",
    "Wakeboard/Packages/Youth": "Watersport/Wakeboard/Package Deals",
    "Wakeboard/Surf/Accessory": "Watersport/Wakeboard/Accessory",
    "Wakeboard/Surf/Bag": "Watersport/Wakeboard/Accessory",
    "Wakeboard/Wakeskate": "Watersport/Wakesurf",
    "Wakeboard/Wakesurfs": "Watersport/Wakesurf",
    "Watersport/Kneeboard/Board": "Watersport/Kneeboard",
    "Watersport/Rashguard/Mens": "Watersport/Outfit/Rashguard",
    "Watersport/Rashguard/Womens": "Watersport/Outfit/Rashguard",
    "Watersport/Ski/Accessory": "Watersport/Water Ski/Accessory",
    "Watersport/Ski/Bag": "Watersport/Water Ski/Accessory",
    "Watersport/Ski/Bindings": "Watersport/Water Ski/Accessory",
    "Watersport/Ski/Combo": "Watersport/Water Ski/Combo",
    "Watersport/Ski/Handle": "Watersport/Water Ski/Handle",
    "Watersport/Ski/Single": "Watersport/Water Ski/Single",
    "Watersport/Towable/Accessory": "Watersport/Towable/Accessory",
    "Watersport/Towable/Tube": "Watersport/Towable/Tube",
    "Watersport/Wetsuit/Mens": "Watersport/Outfit/Wetsuit",
    "Watersport/Wetsuit/Womens": "Watersport/Outfit/Wetsuit",
    "Watersport/Wetsuit/Youth": "Watersport/Outfit/Wetsuit",
    "Winter/Equipment": "Misc",
    "Women/Outerwear/Suit": "Outerwear/Suit",
    "Womens/Baselayer/Bottom": "Outerwear/Base Layer/Women",
    "Womens/Baselayer/Suit": "Outerwear/Base Layer/Women",
    "Womens/Baselayer/Top": "Outerwear/Base Layer/Women",
    "Womens/Lifestyle/Accessory": "Lifestyle/Women/Accessory",
    "Womens/Lifestyle/Dress": "Lifestyle/Women/Dress",
    "Womens/Lifestyle/Jacket": "Lifestyle/Women/Jacket",
    "Womens/Lifestyle/Jumpsuit": "Lifestyle/Women/Pants",
    "Womens/Lifestyle/Pants": "Lifestyle/Women/Pants",
    "Womens/Lifestyle/Shoes": "Lifestyle/Women/Shoes",
    "Womens/Lifestyle/Shorts": "Lifestyle/Women/Shorts",
    "Womens/Lifestyle/Top": "Lifestyle/Women/Tops",
    "Womens/Midlayer": "Outerwear/Midlayer/Women",
    "Womens/Outerwear/Gloves": "Outerwear/Gloves/Women",
    "Womens/Outerwear/Jacket": "Outerwear/Jacket/Women",
    "Womens/Outerwear/Mittens": "Outerwear/Mittens/Women",
    "Womens/Outerwear/Pants": "Outerwear/Pants/Women",
    "Womens/Swimwear": "Lifestyle/Women/Swimwear",
    "Youth/Baselayer/Bottom": "Outerwear/Base Layer/Youth",
    "Youth/Baselayer/Suit": "Outerwear/Base Layer/Youth",
    "Youth/Baselayer/Top": "Outerwear/Base Layer/Youth",
    "Youth/Outerwear/Gloves": "Outerwear/Gloves/Youth",
    "Youth/Outerwear/Jacket": "Outerwear/Jacket/Youth",
    "Youth/Outerwear/Mittens": "Outerwear/Mittens/Youth",
    "Youth/Outerwear/Pants": "Outerwear/Pants/Youth",
    "Clearance/Climbing": "Clearance/Climbing",
    "Clearance/Headwear": "Clearance/Headwear",
    "Clearance/Water Sports": "Clearance/Water Sports",
    "Clearance/Outerwear": "Clearance/Outerwear",
    "Clearance/Headwear": "Clearance/Headwear",
    "Clearance/Ski": "Clearance/Ski",
    "Clearance/Ski/Bindings": "Clearance/Ski/Bindings",
    "Clearance/Ski/Boots": "Clearance/Ski/Boots",
    "Clearance/Ski": "Clearance/Ski",
    "Clearance/Ski/Youth": "Clearance/Ski/Youth",
    "Clearance/Snowboard": "Clearance/Snowboard",
    "Clearance/Snowboard/Boots": "Clearance/Snowboard/Boots",
    "Clearance/Snowboard": "Clearance/Snowboard",
    "Clearance/Snowboard/Youth": "Clearance/Snowbaord/Youth",
    "Clearance/Snowshoe": "Clearance/Snowshoe",
    "Clearance/Snowshoe/Youth": "Clearance/Snowshoe/Youth",
    "Clearance/SUP": "Clearance/SUP",
    "Clearance/Water Sports": "Clearance/Water Sports",
    "Clearance/X-Country": "Clearance/X-Country",
}

clearance_map = {
    "CLBAXE": "Clearance/Climbing",
    "CLBBOO": "Clearance/Climbing",
    "CLBCRA": "Clearance/Climbing",
    "CLBHEL": "Clearance/Climbing",
    "CLBPRT": "Clearance/Climbing",
    "EYEGOG": "Clearance/Headwear",
    "HEL": "Clearance/Headwear",
    "KAYADU": "Clearance/Water Sports",
    "LIFADU": "Clearance/Water Sports",
    "OUTJKT": "Clearance/Outerwear",
    "OUTPNT": "Clearance/Outerwear",
    "SAFHEL": "Clearance/Headwear",
    "SKI": "Clearance/Ski",
    "SKIADU": "Clearance/Ski",
    "SKIBIN": "Clearance/Ski/Bindings",
    "SKIBND": "Clearance/Ski/Bindings",
    "SKIBOO": "Clearance/Ski/Boots",
    "SKIDEM": "Clearance/Ski",
    "SKIPOL": "Clearance/Ski",
    "SKISKI": "Clearance/Ski",
    "SKIYOU": "Clearance/Ski/Youth",
    "SNBADU": "Clearance/Snowboard",
    "SNBBND": "Clearance/Snowboard",
    "SNBBOO": "Clearance/Snowboard/Boots",
    "SNBBRD": "Clearance/Snowboard",
    "SNBDEM": "Clearance/Snowboard",
    "SNBYOU": "Clearance/Snowbaord/Youth",
    "SNO": "Clearance/Snowshoe",
    "SNOBOO": "Clearance/Snowshoe",
    "SNOYOU": "Clearance/Snowshoe/Youth",
    "SUPADU": "Clearance/SUP",
    "WAKBRD": "Clearance/Water Sports",
    "WAKDEM": "Clearance/Water Sports",
    "WAKWSF": "Clearance/Water Sports",
    "WATSKI": "Clearance/Water Sports",
    "WATWAK": "Clearance/Water Sports",
    "XCSBOO": "Clearance/X-Country",
    "XCSPOL": "Clearance/X-Country",
    "XCSSKI": "Clearance/X-Country",
}

to_clearance_map = {
    "6916": "6916",
    "6952": "7063",
    "7033": "7107",
    "7021": "7108",
    "6953": "7109",
    "6964": "7064",
    "7015": "7110",
    "7059": "7111",
    "6993": "7112",
    "6929": "7065",
    "7026": "7113",
    "7025": "7114",
    "7024": "7115",
    "6930": "7116",
    "7020": "7066",
    "6914": "7067",
    "7011": "7117",
    "6915": "7118",
    "6960": "7068",
    "6961": "7119",
    "7045": "7120",
    "7057": "7069",
    "6932": "7070",
    "6935": "7121",
    "6956": "7122",
    "6933": "7123",
    "6967": "7071",
    "6977": "7124",
    "6981": "7125",
    "6968": "7126",
    "6987": "7072",
    "7028": "7127",
    "7034": "7128",
    "7041": "7129",
    "6997": "7073",
    "7040": "7130",
    "6998": "7131",
    "7058": "7132",
    "7053": "7133",
    "7035": "7074",
    "6972": "7075",
    "6989": "7134",
    "6973": "7135",
    "7054": "7136",
    "7036": "7137",
    "7012": "7076",
    "7017": "7138",
    "7037": "7139",
    "7013": "7140",
    "6939": "7077",
    "6940": "7141",
    "6990": "7142",
    "6982": "7143",
    "6957": "7078",
    "7029": "7144",
    "7043": "7145",
    "6946": "7079",
    "7016": "7146",
    "7023": "7147",
    "6947": "7148",
    "6978": "7080",
    "7004": "7149",
    "7022": "7150",
    "7032": "7151",
    "6962": "7081",
    "7018": "7152",
    "7039": "7153",
    "6974": "7082",
    "6992": "7154",
    "6975": "7155",
    "7007": "7083",
    "6948": "7085",
    "6951": "7156",
    "7006": "7157",
    "6949": "7158",
    "6920": "7086",
    "7052": "7159",
    "7008": "7160",
    "6976": "7161",
    "6921": "7162",
    "7046": "7163",
    "6934": "7164",
    "6958": "7087",
    "6969": "7165",
    "7009": "7166",
    "7002": "7167",
    "6979": "7168",
    "7030": "7169",
    "7000": "7170",
    "6959": "7171",
    "7042": "7172",
    "6963": "7088",
    "6927": "7089",
    "6928": "7173",
    "7027": "7174",
    "7001": "7090",
    "6996": "7091",
    "6986": "7092",
    "7048": "7093",
    "7055": "7094",
    "7044": "7095",
    "7050": "7096",
    "6943": "7097",
    "6985": "7175",
    "6950": "7176",
    "6994": "7177",
    "6924": "7098",
    "7056": "7178",
    "6966": "7179",
    "6925": "7180",
    "7049": "7181",
    "6941": "7099",
    "6942": "7182",
    "6984": "7183",
    "6988": "7184",
    "7010": "7185",
    "7019": "7100",
    "6918": "7101",
    "6954": "7102",
    "7038": "7103",
    "6922": "7104",
    "7047": "7186",
    "6923": "7187",
    "6944": "7105",
    "6999": "7188",
    "6971": "7189",
    "6980": "7106",
}


to_ebay_map = {
    "7033": "42814",
    "7021": "42814",
    "6953": "42814",
    "7015": "21238",
    "7059": "21238",
    "6993": "21238",
    "7026": "16061",
    "7025": "119237",
    "7024": "21241",
    "6930": "21240",
    "7020": "36260",
    "7011": "58129",
    "6915": "58129",
    "6961": "97064",
    "7045": "97064",
    "7057": "1302",
    "6935": "93825",
    "6956": "93825",
    "6933": "93825",
    "6977": "21248",
    "6981": "21248",
    "6968": "21248",
    "7028": "36292",
    "7034": "36292",
    "7041": "36292",
    "7040": "21229",
    "6998": "21229",
    "7058": "21229",
    "7053": "21229",
    "7035": "159155",
    "6989": "21230",
    "6973": "21230",
    "7054": "21230",
    "7036": "21230",
    "7017": "26346",
    "7037": "26346",
    "7013": "26346",
    "6940": "36261",
    "6990": "36261",
    "6982": "36261",
    "7029": "179012",
    "7043": "179012",
    "7016": "62171",
    "7023": "62171",
    "6947": "62171",
    "7004": "62172",
    "7022": "62172",
    "7032": "62172",
    "7018": "62172",
    "7039": "62172",
    "6992": "62175",
    "6975": "62175",
    "7007": "62178",
    "6951": "179241",
    "7006": "79720",
    "6949": "45246",
    "7052": "1060",
    "7008": "57988",
    "6976": "57989",
    "6921": "313",
    "7046": "15689",
    "6934": "313",
    "6969": "1063",
    "7009": "314",
    "7002": "63862",
    "6979": "63863",
    "7030": "314",
    "7000": "11555",
    "6959": "63867",
    "7042": "314",
    "6963": "1063",
    "6928": "159067",
    "7027": "159068",
    "7001": "36317",
    "6996": "16264",
    "6986": "16263",
    "7048": "36625",
    "7055": "36634",
    "7044": "23830",
    "7050": "16265",
    "6985": "15272",
    "6950": "47363",
    "6994": "47363",
    "7056": "15272",
    "6966": "71175",
    "6925": "74048",
    "7049": "71175",
    "6942": "15262",
    "6984": "15262",
    "6988": "15262",
    "7010": "15262",
    "7019": "159151",
    "6918": "159151",
    "7038": "36123",
    "7047": "15272",
    "6923": "71169",
    "6999": "114256",
    "6971": "29574",
}


bc_ebay_category_map = {
    #     |-- Ski: 6913
    # |   |-- Skis: 6952
    # |   |   |-- Men: 7033
    # |   |   |-- Women: 7021
    # |   |   +-- Youth: 6953
    # |   |-- Bindings: 6964
    # |   |   |-- Men: 7015
    # |   |   |-- Women: 7059
    # |   |   +-- Youth: 6993
    # |   |-- Boots: 6929
    # |   |   |-- Men: 7026
    # |   |   |-- Parts: 7025
    # |   |   |-- Women: 7024
    # |   |   +-- Youth: 6930
    # |   |-- Helmets: 7020
    # |   |-- Poles: 6914
    # |   |   |-- Adult: 7011
    # |   |   +-- Youth: 6915
    # |   |-- Socks: 6960
    # |   |   |-- Adult: 6961
    # |   |   +-- Youth: 7045
    # |   +-- Accessory: 7057
    7033: 42814,
    7021: 42814,
    6953: 42814,
    7015: 21238,
    7059: 21238,
    6993: 21238,
    7026: 16061,
    7025: 119237,
    7024: 21241,
    6930: 21240,
    7020: 36260,
    7011: 58129,
    6915: 58129,
    6961: 97064,
    7045: 97064,
    7057: 1302,
    # |-- Snowboard: 6931
    # |   |-- Board: 6932
    # |   |   |-- Men: 6935
    # |   |   |-- Women: 6956
    # |   |   +-- Youth: 6933
    # |   |-- Bindings: 6967
    # |   |   |-- Adult: 6977
    # |   |   |-- Women: 6981
    # |   |   +-- Youth: 6968
    # |   |-- Boots: 6987
    # |   |   |-- Men: 7028
    # |   |   |-- Women: 7034
    # |   |   +-- Youth: 7041
    # |   |-- Bags: 6997
    # |   |   |-- Backpack: 7040
    # |   |   |-- Board: 6998
    # |   |   |-- Travel: 7058
    # |   |   +-- Wheel: 7053
    # |   +-- Accessory: 7035
    6935: 93825,
    6956: 93825,
    6933: 93825,
    6977: 21248,
    6981: 21248,
    6968: 21248,
    7028: 36292,
    7034: 36292,
    7041: 36292,
    7040: 21229,
    6998: 21229,
    7058: 21229,
    7053: 21229,
    7035: 159155,
    # |-- Outerwear: 6938
    # |   |-- Goggles: 6972
    # |   |   |-- Accessory: 6989
    # |   |   |-- Adult: 6973
    # |   |   |-- Women: 7054
    # |   |   +-- Youth: 7036
    # |   |-- Jacket: 7012
    # |   |   |-- Men: 7017
    # |   |   |-- Women: 7037
    # |   |   +-- Youth: 7013
    # |   |-- Pants: 6939
    # |   |   |-- Men: 6940
    # |   |   |-- Women: 6990
    # |   |   +-- Youth: 6982
    # |   |-- Midlayer: 6957
    # |   |   |-- Men: 7029
    # |   |   +-- Women: 7043
    # |   |-- Base Layer: 6946
    # |   |   |-- Men: 7016
    # |   |   |-- Women: 7023
    # |   |   +-- Youth: 6947
    # |   |-- Gloves: 6978
    # |   |   |-- Men: 7004
    # |   |   |-- Women: 7022
    # |   |   +-- Youth: 7032
    # |   |-- Mittens: 6962
    # |   |   |-- Women: 7018
    # |   |   +-- Youth: 7039
    # |   |-- Headwear: 6974
    # |   |   |-- Beanie: 6992
    # |   |   +-- Facemask: 6975
    # |   +-- Suit: 7007
    6989: 21230,
    6973: 21230,
    7054: 21230,
    7036: 21230,
    7017: 26346,
    7037: 26346,
    7013: 26346,
    6940: 36261,
    6990: 36261,
    6982: 36261,
    7029: 179012,
    7043: 179012,
    7016: 62171,
    7023: 62171,
    6947: 62171,
    7004: 62172,
    7022: 62172,
    7032: 62172,
    7018: 62172,
    7039: 62172,
    6992: 62175,
    6975: 62175,
    7007: 62178,
    # |-- Lifestyle: 6919
    # |   |-- Sunglasses: 6948
    # |   |   |-- Accessory: 6951
    # |   |   |-- Unisex: 7006
    # |   |   +-- Womens: 6949
    # |   |-- Men: 6920
    # |   |   |-- Accessory: 7052
    # |   |   |-- Jacket: 7008
    # |   |   |-- Pants: 6976
    # |   |   |-- Shoes: 6921
    # |   |   |-- Shorts: 7046
    # |   |   +-- Tops: 6934
    # |   |-- Women: 6958
    # |   |   |-- Accessory: 6969
    # |   |   |-- Dress: 7009
    # |   |   |-- Jacket: 7002
    # |   |   |-- Pants: 6979
    # |   |   |-- Shoes: 7030
    # |   |   |-- Shorts: 7000
    # |   |   |-- Swimwear: 6959
    # |   |   +-- Tops: 7042
    # |   +-- Accessory: 6963
    6951: 179241,
    7006: 79720,
    6949: 45246,
    7052: 1060,
    7008: 57988,
    6976: 57989,
    6921: 313,
    7046: 15689,
    6934: 313,
    6969: 1063,
    7009: 314,
    7002: 63862,
    6979: 63863,
    7030: 314,
    7000: 11555,
    6959: 63867,
    7042: 314,
    6963: 1063,
    # |-- Skate: 6926
    # |   |-- Shoes: 6927
    # |   |   |-- Men: 6928
    # |   |   +-- Women: 7027
    # |   |-- Helmets: 7001
    # |   |-- Completes: 6996
    # |   |-- Decks: 6986
    # |   |-- Trucks: 7048
    # |   |-- Bearings: 7055
    # |   |-- Wheels: 7044
    # |   +-- Accessory: 7050
    6928: 159067,
    7027: 159068,
    7001: 36317,
    6996: 16264,
    6986: 16263,
    7048: 36625,
    7055: 36634,
    7044: 23830,
    7050: 16265,
    # |-- Watersport: 6917
    # |   |-- Wakeboard: 6943
    # |   |   |-- Accessory: 6985
    # |   |   |-- Board: 6950
    # |   |   +-- Package Deals: 6994
    # |   |-- Water Ski: 6924
    # |   |   |-- Accessory: 7056
    # |   |   |-- Combo: 6966
    # |   |   |-- Handle: 6925
    # |   |   +-- Single: 7049
    # |   |-- Life Jackets: 6941
    # |   |   |-- Dog: 6942
    # |   |   |-- Men: 6984
    # |   |   |-- Women: 6988
    # |   |   +-- Youth: 7010
    # |   |-- Wakesurf: 7019
    # |   |-- Kneeboard: 6918
    # |   |-- Kayak: 7038
    # |   |-- Towable: 6922
    # |   |   |-- Accessory: 7047
    # |   |   +-- Tube: 6923
    # |   +-- Outfit: 6944
    # |       |-- Rashguard: 6999
    # |       +-- Wetsuit: 6971
    6985: 15272,
    6950: 47363,
    6994: 47363,
    7056: 15272,
    6966: 71175,
    6925: 74048,
    7049: 71175,
    6942: 15262,
    6984: 15262,
    6988: 15262,
    7010: 15262,
    7019: 159151,
    6918: 159151,
    7038: 36123,
    7047: 15272,
    6923: 71169,
    6999: 114256,
    6971: 29574,
}
