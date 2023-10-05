import datetime as dt
import pandas as pd
import requests
from secret_info import headers, base, daysAgo
import time
import tqdm


def retry_request_using_response(res):
    r = res.request
    res = requests.request(method=r.method, url=r.url, headers=r.headers)
    return res


def call_iteratively(call, *args):
    res = call(*args)
    if res.status_code == 429:
        s = int(res.headers["X-Rate-Limit-Time-Reset-Ms"]) / 1000
        print(f"{s} seconds until rate-limit rest")
        time.sleep(s)
        print("slept")
        retry_request_using_response(res)
    elif res.ok:
        j = res.json()
        data = j["data"]
        pag = j["meta"]["pagination"]
        for i in tqdm.tqdm(range(2, pag["total_pages"] + 1)):
            subres = call(*args, i)
            if subres.ok:
                data.extend(subres.json()["data"])
        return data


def get_products(last_modified, i=1):
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


def products_since(last_modified):
    data = call_iteratively(get_products, last_modified)
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
    pdf = pd.read_pickle("data/products.pkl")
    if len(pdf) > 0:
        new_p = products_since(
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
            pdf.to_pickle("data/products.pkl")
            return pdf
    else:
        new_p = products_since("1970-01-01")
        new_p.to_pickle("data/products.pkl")
        if new_p is None:
            return pdf
        else:
            return new_p


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


def delete_product(id_):
    h = headers.copy()
    url = base + f"v3/catalog/products/{id_}"
    res = requests.delete(url, headers=h)
    return res


def create_product(data):
    url = base + "v3/catalog/products"
    h = headers.copy()
    h.update({"content-type": "application/json"})
    res = requests.post(url, headers=h, json=data)
    return res


def update_product(id_, data, slow=False):
    responses = []
    url = base + f"v3/catalog/products/{id_}"
    h = headers.copy()
    h.update({"content-type": "application/json"})
    if "variants" not in data:
        res = requests.put(url, headers=h, json=data)
        responses.append(res)
    else:
        variants = data.pop("variants")
        res = requests.put(url, headers=h, json=data)
        responses.append(res)
        for variant_data in variants:
            variant_url = url + f"/variants/{variant_data.pop('id')}"
            res = requests.put(variant_url, headers=h, json=variant_data)
            if slow:
                time.sleep(1)
            else:
                time.sleep(0.1)
            # don't return variant not found res in res array
            # TODO: why tf not?
            if res.status_code != 404:
                responses.append(res)
    return responses


def get_all_brand_ids():
    def get_brands(i=1):
        url = base + "v3/catalog/brands" + f"?limit=50&page={i}"
        res = requests.get(url, headers=headers)
        return res

    data = call_iteratively(get_brands)
    return {d["id"]: d["name"] for d in data}


def create_brand(name):
    """returns brand ID upon creation"""
    url = base + "v3/catalog/brands"
    h = headers.copy()
    h.update({"content-type": "application/json", "accept": "application/json"})
    d = {"name": f"{name}"}
    res = requests.post(url, headers=h, json=d)
    if res.ok:
        return res.json()["data"]["id"]


def get_all_category_ids():
    url = base + "v3/catalog/categories/tree"
    res = requests.get(url, headers=headers)
    cat = {}
    for i in res.json()["data"]:
        cat.update({i["id"]: i["name"]})
        for j in i["children"]:
            cat.update({j["id"]: i["name"] + "/" + j["name"]})
            for k in j["children"]:
                cat.update({k["id"]: i["name"] + "/" + j["name"] + "/" + k["name"]})
    return cat


def create_custom_field(product_id, key, value):
    url = base + f"v3/catalog/products/{product_id}/custom-fields"
    data = {
        "name": key,
        "value": str(value),
    }
    h = headers.copy()
    h.update({"content-type": "application/json"})
    res = requests.post(url, headers=h, json=data)
    return res


def get_custom_field_id(product_id, key):
    url = base + f"v3/catalog/products/{product_id}/custom-fields"
    h = headers.copy()
    res = requests.get(url, headers=h)
    fields = res.json()["data"]
    for d in fields:
        if d["name"] == key:
            return d["id"]


def update_custom_field(product_id, key, value):
    cfid = get_custom_field_id(product_id, key)
    if cfid:
        url = base + f"v3/catalog/products/{product_id}/custom-fields/{cfid}"
        data = {
            "name": key,
            "value": str(value),
        }
        h = headers.copy()
        h.update({"accept": "application/json", "content-type": "application/json"})
        res = requests.put(url, headers=h, json=data)
        return res
    else:
        return create_custom_field(product_id, key, value)
