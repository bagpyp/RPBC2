def product_creation_payload(g):
    product = {}
    g = g.fillna("").to_dict("records")
    r = g[0]
    # what every product gets, from the front row of g
    product.update(
        {
            "type": "physical",
            "weight": 0,
            "categories": [int(r["cat"])],
            "brand_id": int(r["brand"]),
            "name": r["webName"],
            "sale_price": r["pSale"],
            "price": r["pMAP"],
            "list_on_amazon": r["listOnAmazon"],
            "amazon_price": r["pAmazon"],
            "retail_price": r["pMSRP"],
            "sku": r["sku"],
            "description": r["description"],
        }
    )
    product.update({"is_visible": False})
    product_has_images = 0
    if r["image_0_file"] != "":
        product.update({"is_visible": True})
        product_has_images += 1

    for i in range(1, 5):
        if r[f"image_{i}_file"] != "":
            product_has_images += 1

    if product_has_images:
        product.update(
            {
                "images": [
                    {
                        "image_url": "https://www.hillcrestsports.com"
                        + r["image_0_file"],
                        "is_thumbnail": True,
                    }
                ]
                + [
                    {
                        "image_url": "https://www.hillcrestsports.com"
                        + r[f"image_{i}_file"]
                    }
                    for i in range(1, 5)
                    if r[f"image_{i}_file"] != ""
                ]
            }
        )
    if len(g) > 1:
        product.update(
            {
                "search_keywords": ",".join(
                    list(
                        set(
                            (
                                r["CAT"].split("/")
                                + [r["BRAND"], r["sku"]]
                                + [h["sku"].split("-")[-1].lstrip("0") for h in g[1:]]
                                + [h["mpn"] for h in g[1:]]
                            )
                        )
                    )
                ),
                "inventory_tracking": "variant",
            }
        )
        variants = []
        for h in g[1:]:
            variant = {}
            variant.update(
                {
                    "inventory_level": h["qty"],
                    "sale_price": h["pSale"],
                    "price": h["pMAP"],
                    "amazon_price": h["pAmazon"],
                    "retail_price": h["pMSRP"],
                    "upc": h["UPC"],
                    "sku": h["sku"],
                    "mpn": h["mpn"],
                    "option_values": [
                        {"option_display_name": s.title(), "label": h[s]}
                        if h[s] != ""
                        else {"option_display_name": s.title(), "label": "IRRELEVANT"}
                        for s in ["color", "size"]
                    ],
                }
            )

            if h["v_image_url_file"] != "":
                variant.update(
                    {
                        "image_url": "https://www.hillcrestsports.com"
                        + h["v_image_url_file"]
                    }
                )
            variants.append(variant)
        product.update({"variants": variants})
    elif len(g) == 1:
        product.update(
            {
                "search_keywords": ",".join(
                    list(
                        set(
                            r["CAT"].split("/")
                            + [
                                r["BRAND"],
                                r["sku"],
                                r["sku"].split("-")[-1].lstrip("0"),
                            ]
                        )
                    )
                ),
                "inventory_tracking": "product",
                "inventory_level": r["qty"],
                "sale_price": r["pSale"],
                "price": r["pMAP"],
                "amazon_price": r["pAmazon"],
                "retail_price": r["pMSRP"],
                "mpn": r["mpn"],
                "upc": r["UPC"],
                "custom_fields": [
                    {"name": s.title(), "value": r[s]}
                    for s in ["color", "size"]
                    if r[s] != ""
                ],
            }
        )
    return product


def product_update_payload(g):
    product = {}
    g = g.fillna("").to_dict("records")
    r = g[0]
    product.update(
        {
            "id": r["p_id"],
            "inventory_level": r["qty"],
            "sale_price": r["pSale"],
            "price": r["pMAP"],
            "list_on_amazon": r["listOnAmazon"],
            "amazon_price": r["pAmazon"],
            "retail_price": r["pMSRP"],
        }
    )
    if r["clearance_cat"] != "":
        product.update({"categories": [int(r["cat"]), int(r["clearance_cat"])]})
    else:
        product.update({"categories": [int(r["cat"])]})
    if r["image_0"] != "":
        product.update({"is_visible": True})
    elif r["image_0"] == "":
        product.update({"is_visible": False})
    if len(g) > 1:
        variants = []
        for h in g[1:]:
            variant = {}
            variant.update(
                {
                    "id": h["v_id"],
                    "inventory_level": h["qty"],
                    "price": h["pMAP"],
                    "amazon_price": h["pAmazon"],
                    "sale_price": h["pSale"],
                    "retail_price": h["pMSRP"],
                }
            )
            variants.append(variant)
        product.update({"variants": variants})
    return product
