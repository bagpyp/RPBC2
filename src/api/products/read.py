import datetime as dt

import pandas as pd
import requests
from src.api.request_utils import call_iteratively

from secret_info import headers, base, daysAgo


def get_product_by_sku(sku):
    h = headers.copy()
    url = base + f"v3/catalog/products?sku={sku}"
    res = requests.get(url, headers=h)
    return res


def get_product_by_name(name_):
    h = headers.copy()
    url = base + f"v3/catalog/products?name={name_}"
    res = requests.get(url, headers=h)
    return res


def _get_products(last_modified, i=1):
    url = (
        base
        + "v3/catalog/products"
        + f"?limit=10&page={i}"
        + "&include=variants,images"
    )
    # TODO: actually call only products using last_modified_date
    # + f'&date_modified:min={last_modified}'
    res = requests.get(url, headers=headers)
    return res


def _products_since(last_modified):
    data = call_iteratively(_get_products, last_modified)
    products = []

    for product in data:
        product_images = {}
        for i, image in enumerate(product["images"]):
            product_images.update({f"image_{i}": image["url_standard"]})

        if product["variants"]:
            for variant in product["variants"]:
                product_record_info = {}
                product_record_info.update(product_images)

                product_record_info.update(
                    p_id=product["id"],
                    p_name=product["name"],
                    p_sku=product["sku"],
                    p_price=product["price"],
                    p_cost_price=product["cost_price"],
                    p_retail_price=product["retail_price"],
                    p_sale_price=product["sale_price"],
                    p_map_price=product["map_price"],
                    p_calculated_price=product["calculated_price"],
                    p_categories=product["categories"],
                    p_brand_id=product["brand_id"],
                    p_option_set_id=product["option_set_id"],
                    p_option_set_display=product["option_set_display"],
                    p_inventory_level=product["inventory_level"],
                    p_inventory_tracking=product["inventory_tracking"],
                    p_is_visible=product["is_visible"],
                    p_upc=product["upc"],
                    p_mpn=product["mpn"],
                    p_search_keywords=product["search_keywords"],
                    p_date_created=product["date_created"],
                    p_date_modified=product["date_modified"],
                    p_view_count=product["view_count"],
                    p_preorder_release_date=product["preorder_release_date"],
                    p_is_preorder_only=product["is_preorder_only"],
                    p_base_variant_id=product["base_variant_id"],
                    p_description=product["description"],
                    v_id=variant["id"],
                    v_sku=variant["sku"],
                    v_sku_id=variant["sku_id"],
                    v_price=variant["price"],
                    v_cost_price=variant["cost_price"],
                    v_retail_price=variant["retail_price"],
                    v_sale_price=variant["sale_price"],
                    v_map_price=variant["map_price"],
                    v_calculated_price=variant["calculated_price"],
                    v_image_url=variant["image_url"],
                    v_upc=variant["upc"],
                    v_mpn=variant["mpn"],
                    v_inventory_level=variant["inventory_level"],
                )

                if variant["option_values"]:
                    product_option_data = {}
                    for option in variant["option_values"]:
                        pre = option.pop("option_display_name").lower() + "_"
                        product_option_data.update(
                            {pre + k: v for k, v in option.items()}
                        )
                    product_record_info.update(product_option_data)

                products.append(product_record_info)

        else:  # product does not have variants
            product_record_info = {}
            product_record_info.update(product_images)

            # only append product information (chapstick type product)
            product_record_info.update(
                p_id=product["id"],
                p_name=product["name"],
                p_sku=product["sku"],
                p_price=product["price"],
                p_cost_price=product["cost_price"],
                p_retail_price=product["retail_price"],
                p_sale_price=product["sale_price"],
                p_map_price=product["map_price"],
                p_calculated_price=product["calculated_price"],
                p_categories=product["categories"],
                p_brand_id=product["brand_id"],
                p_option_set_id=product["option_set_id"],
                p_option_set_display=product["option_set_display"],
                p_inventory_level=product["inventory_level"],
                p_inventory_tracking=product["inventory_tracking"],
                p_is_visible=product["is_visible"],
                p_upc=product["upc"],
                p_mpn=product["mpn"],
                p_search_keywords=product["search_keywords"],
                p_date_created=product["date_created"],
                p_date_modified=product["date_modified"],
                p_view_count=product["view_count"],
                p_preorder_release_date=product["preorder_release_date"],
                p_is_preorder_only=product["is_preorder_only"],
                p_base_variant_id=product["base_variant_id"],
                p_description=product["description"],
            )

            products.append(product_record_info)

    if products:
        df = pd.DataFrame(products)
        df.loc[:, "p_categories"] = df.p_categories.apply(
            lambda x: ",".join([str(y) for y in x])
        )
        return df


def updated_products():
    pdf = pd.read_pickle("../../../data/products.pkl")
    if len(pdf) > 0:
        new_p = _products_since(
            (dt.datetime.now() - dt.timedelta(days=daysAgo)).strftime(
                "%Y-%m-%dT%H:%M:%S-07:00"
            )
        )
        # this is where products are getting duplicated, in all but v_id
        if len(new_p) > 0:
            pdf = pdf.set_index("v_id")
            new_p = new_p.set_index("v_id")
            pdf.update(new_p)
            pdf = pd.concat([pdf, new_p[~new_p.index.isin(pdf.index)]])
            pdf = pdf.reset_index()
            # this is where we should remove all items with duplicated v_skus
            pdf = pdf[pdf.v_id.isin(pdf.groupby("v_sku", sort=False).v_id.max())]
            # keeping only those whose v_id is... LARGEST
            pdf.to_pickle("../../../data/products.pkl")
            return pdf
    else:
        new_p = _products_since("1970-01-01")
        new_p.to_pickle("../../../data/products.pkl")
        if new_p is None:
            return pdf
        else:
            return new_p
