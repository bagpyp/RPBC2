import pandas as pd

from src.api.products.get_all_products import get_all_products
from src.util import DATA_DIR


def pull_product_data_from_big_commerce():
    print("Pulling product data from BigCommerce...")

    data = get_all_products()

    products = []
    for product in data:
        # representative data
        product_record_info = {}
        product_record_info.update(
            p_id=product["id"],
            p_name=product["name"],
            p_sku=product["sku"],
            p_price=product["price"],
            p_qty=product["inventory_level"],
            p_categories=product["categories"],
            p_brand_id=product["brand_id"],
            p_is_visible=product["is_visible"],
            p_description=product["description"],
        )
        # representative images
        product_images = {}
        for i, image in enumerate(product["images"]):
            if i < 11:  # cap 10 images and base image
                product_images.update({f"image_{i}": image["url_standard"]})
        product_record_info.update(product_images)
        # representative custom_fields
        custom_fields = product.get("custom_fields", [])
        for cf in custom_fields:
            if cf["name"] == "eBay Category ID":
                product_record_info["cf_ebay_category"] = cf["value"]
            elif cf["name"] == "eBay Sale Price":
                product_record_info["cf_ebay_price"] = cf["value"]
            elif cf["name"] == "Amazon Status":
                product_record_info["cf_amazon_status"] = cf["value"] == "Enabled"
            elif cf["name"] == "eBay Status":
                product_record_info["cf_ebay_status"] = cf["value"] == "Enabled"
            elif cf["name"] == "WalMart Status":
                product_record_info["cf_walmart_status"] = cf["value"] == "-1"
        # variants
        if product["variants"]:
            for variant in product["variants"]:
                variant_record_info = product_record_info.copy()
                variant_record_info.update(product_images)

                variant_record_info.update(
                    v_id=variant["id"],
                    v_sku=variant["sku"],
                    v_image_url=variant["image_url"],
                    v_qty=variant["inventory_level"],
                )
                products.append(variant_record_info)
        else:
            products.append(product_record_info)

    pdf = pd.DataFrame(products)
    pdf.loc[:, "p_categories"] = pdf.p_categories.apply(
        lambda x: ",".join([str(y) for y in x])
    )
    pdf.loc[:, "p_id"] = pdf.p_id.astype(int).astype(str)
    pdf.loc[:, "v_id"] = pdf.v_id.astype(int).astype(str)
    pdf.to_pickle(f"{DATA_DIR}/products.pkl")
    # TODO: fuck this idea, returning something different from what you pickle!
    return pdf.reset_index()


if __name__ == "__main__":
    pull_product_data_from_big_commerce()
