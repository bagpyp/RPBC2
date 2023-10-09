import pandas as pd
import requests

from config import headers, base
from src.api.request_utils import call_iteratively
from src.util.path_utils import DATA_DIR


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


def _get_products(i=1):
    url = (
        base
        + "v3/catalog/products"
        + f"?limit=10&page={i}"
        + "&include=variants,images"
    )
    res = requests.get(url, headers=headers)
    return res


def get_all_product_data_from_big_commerce():
    data = call_iteratively(_get_products)

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

    pdf = pd.DataFrame(products)
    pdf.loc[:, "p_categories"] = pdf.p_categories.apply(
        lambda x: ",".join([str(y) for y in x])
    )
    pdf.loc[:, "p_id"] = pdf.p_id.astype(int).astype(str)
    pdf.loc[:, "v_id"] = pdf.v_id.astype(int).astype(str)
    pdf.to_pickle(f"{DATA_DIR}/products.pkl")
    return pdf
