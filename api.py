# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 10:14:03 2020

@author: Web
"""

import datetime as dt
import pandas as pd
import requests
from secret_info import headers, base, daysAgo
import time
import tqdm


# fucking rate limits
def retry(res):
    r = res.request
    res = requests.request(method=r.method, url=r.url, headers=r.headers)
    return res


# pagination helper


def iterCall(call, *args):
    res = call(*args)
    if res.status_code == 429:
        s = int(res.headers["X-Rate-Limit-Time-Reset-Ms"]) / 1000
        print(f"{s} seconds until rate-limit rest")
        time.sleep(s)
        print("slept")
        retry(res)
    elif res.ok:
        j = res.json()
        data = j["data"]
        pag = j["meta"]["pagination"]
        for i in tqdm.tqdm(range(2, pag["total_pages"] + 1)):
            subres = call(*args, i)
            if subres.ok:
                data.extend(subres.json()["data"])
        return data


# products


def getProducts(last_modified, i=1):
    url = (
        base
        + "v3/catalog/products"
        + f"?limit=10&page={i}"
        + "&include=variants,images"
    )
    # trying without, FIX LATER
    # + f'&date_modified:min={last_modified}'
    res = requests.get(url, headers=headers)
    return res


def products_since(last_modified):
    # data = getProducts(last_modified).json()['data']
    data = iterCall(getProducts, last_modified)
    listOfDicts = []
    # do i need if product['images']? if so, how if, if else below??
    if data:
        for product in data:
            imgs = {}
            i = 0
            for image in product["images"]:
                imgs.update({f"image_{i}": image["url_standard"]})
                i += 1
            if product["variants"]:
                for variant in product["variants"]:
                    dictOfInfo = {}
                    # append v_ information to list
                    dictOfInfo.update(
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
                    dictOfInfo.update(imgs)
                    if variant["option_values"]:
                        optionInfo = {}
                        for option in variant["option_values"]:
                            pre = option.pop("option_display_name").lower() + "_"
                            optionInfo.update({pre + k: v for k, v in option.items()})
                        dictOfInfo.update(optionInfo)
                        listOfDicts.append(dictOfInfo)
                    else:
                        listOfDicts.append(dictOfInfo)
            else:
                dictOfInfo = {}
                # only append product information
                dictOfInfo.update(
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
                dictOfInfo.update(imgs)
                listOfDicts.append(dictOfInfo)
        if listOfDicts:
            df = pd.DataFrame(listOfDicts)
            df.loc[:, "p_categories"] = df.p_categories.apply(
                lambda x: ",".join([str(y) for y in x])
            )
            return df


# REVIEW!!
# function to update product pickle
def updatedProducts():
    # RERUN IF PKL LOST
    # p = products_since('1970-01-01')
    # p.to_pickle('products.pkl')
    p = pd.read_pickle("data/products.pkl")
    if len(p) > 0:
        new_p = products_since(
            (dt.datetime.now() - dt.timedelta(days=daysAgo)).strftime(
                "%Y-%m-%dT%H:%M:%S-07:00"
            )
        )
        # this is where products are getting duplicated, in all but v_id
        if len(new_p) > 0:
            p = p.set_index("v_id")
            new_p = new_p.set_index("v_id")
            p.update(new_p)
            p = pd.concat([p, new_p[~new_p.index.isin(p.index)]])
            p = p.reset_index()
            # this is where we should remove all items with duplicated v_skus
            p = p[p.v_id.isin(p.groupby("v_sku", sort=False).v_id.max())]
            # keeping only those whose v_id is... LARGEST
            p.to_pickle("products.pkl")
            return p
    else:
        new_p = products_since("1970-01-01")
        new_p.to_pickle("products.pkl")
        if new_p is None:
            return p
        else:
            return new_p


def getProductBySku(sku):
    h = headers.copy()
    url = base + f"v3/catalog/products?sku={sku}"
    res = requests.get(url, headers=h)
    return res


def getProductByName(name_):
    h = headers.copy()
    url = base + f"v3/catalog/products?name={name_}"
    res = requests.get(url, headers=h)
    return res


# delete product by ID
def deleteProduct(id_):
    h = headers.copy()
    url = base + f"v3/catalog/products/{id_}"
    res = requests.delete(url, headers=h)
    return res


# create product using built payload, `data`
def createProduct(data):
    url = base + "v3/catalog/products"
    h = headers.copy()
    h.update({"content-type": "application/json"})
    res = requests.post(url, headers=h, json=data)
    return res


# update product via payload, `data`
def updateProduct(id_, data, slow=False):
    responses = []
    url = base + f"v3/catalog/products/{id_}"
    h = headers.copy()
    h.update({"content-type": "application/json"})
    if "variants" not in data:
        res = requests.put(url, headers=h, json=data)
        responses.append(res)
        return responses
    else:
        variants = data.pop("variants")
        res = requests.put(url, headers=h, json=data)
        responses.append(res)
        for v in variants:
            vUrl = url + f"/variants/{v.pop('id')}"
            res = requests.put(vUrl, headers=h, json=v)
            if slow:
                time.sleep(1)
            else:
                time.sleep(0.1)
            # don't return variant not found res in res array
            if res.status_code != 404:
                responses.append(res)
        return responses


# brands


def brandIDs():
    def getBrands(i=1):
        url = base + "v3/catalog/brands" + f"?limit=50&page={i}"
        res = requests.get(url, headers=headers)
        return res

    data = iterCall(getBrands)
    return {d["id"]: d["name"] for d in data}


def createBrand(name):
    """returns brand ID upon creation"""
    url = base + "v3/catalog/brands"
    h = headers.copy()
    h.update({"content-type": "application/json", "accept": "application/json"})
    d = {"name": f"{name}"}
    res = requests.post(url, headers=h, json=d)
    if res.ok:
        return res.json()["data"]["id"]


# categories


def categoryIDs():
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


def createMetafield(
    product_id,
    key,
    value,
    description="a metafield",
    namespace="general",
    permission_set="read",
):
    # permission_set in [read, write, app_only,
    # read_and_sf_access, write_and_sf_access]
    url = base + f"v3/catalog/products/{product_id}/metafields"
    data = {
        "key": key,
        "value": value,
        "description": description,
        "namespace": namespace,
        "permission_set": permission_set,
    }
    h = headers.copy()
    h.update({"content-type": "application/json"})
    res = requests.post(url, headers=h, json=data)
    return res


def createCustomField(product_id, key, value):
    url = base + f"v3/catalog/products/{product_id}/custom-fields"
    data = {
        "name": key,
        "value": str(value),
    }
    h = headers.copy()
    h.update({"content-type": "application/json"})
    res = requests.post(url, headers=h, json=data)
    return res


def getCustomFieldId(product_id, key):
    url = base + f"v3/catalog/products/{product_id}/custom-fields"
    h = headers.copy()
    res = requests.get(url, headers=h)
    fields = res.json()["data"]
    for d in fields:
        if d["name"] == key:
            return d["id"]


def updateCustomField(product_id, key, value):
    cfid = getCustomFieldId(product_id, key)
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
        return createCustomField(product_id, key, value)
