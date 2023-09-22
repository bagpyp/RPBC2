# %%
# -*- coding: utf-8 -*-

from anytree import Node, RenderTree
from numpy import where
import pandas as pd

pd.options.mode.chained_assignment = None
pd.options.display.max_rows = 150
pd.options.display.max_columns = 50
pd.options.display.width = 180
pd.options.display.max_colwidth = 30
import requests
from secret_info import headers, base
import time
from maps import to_clearance_map


def pt(root):
    print(RenderTree(root))


def categoryTree():
    url = base + "v3/catalog/categories/tree"
    res = requests.get(url, headers=headers)
    cat = res.json()["data"]
    root = Node("Categories")
    for a in cat:
        A = Node(a["name"], root, id=a["id"])
        for b in a["children"]:
            B = Node(b["name"], A, id=b["id"])
            for c in b["children"]:
                Node(c["name"], B, id=c["id"])
    return root


def copyTree(root, name="copy"):
    copy = Node(name)
    for child in root.children:
        if child.is_leaf:
            Node(child.name, copy, old_id=child.id)
        else:
            for grandchild in child.children:
                adjoin = Node(
                    child.name + "-" + grandchild.name, copy, old_id=grandchild.id
                )
                for greatgrandchild in grandchild.children:
                    Node(greatgrandchild.name, adjoin, old_id=greatgrandchild.id)
    return copy


# will need to change to true
def createCategory(name="", parent_id=0, is_visible=False):
    # parent_id:
    # To create a child category, set the parent_id to the parent category.
    # To create a top level category, set the parent_id to 0.
    # returns id of new category or None if unsuccessful
    data = {
        "name": name,
        "parent_id": parent_id,
        "is_visible": is_visible,
    }
    url = base + "v3/catalog/categories"
    headers.update({"content-type": "application/json"})
    res = requests.post(url, headers=headers, json=data)
    if res.ok:
        return res.json()["data"]["id"]
    else:
        return None


# %%
year = time.gmtime().tm_year
month = time.gmtime().tm_mon
# only showing last 3 years - (3)
# winter product becomes old in May - (4)
# summer product becomes old in November - (11)
old = [
    f"{n - 1}-{n}"
    for n in range(
        int(str((year + 1) - 3)[2:]) + int(month >= 5),
        int(str(year)[2:]) + int(month >= 5),
    )
] + [
    str(i)
    for i in range(int(str(year - 3)) + int(month >= 5), int(year) + int(month >= 11))
]
new = [
    f"{(int(str(year)[-2:]) - 1) + int(month > 5)}"
    + f"-{(int(str(year)[-2:])) + int(month > 5)}",
    f"{year + int(month > 11)}",
]

df = pd.read_pickle("data/moreReady.pkl")
df["is_old"] = df.webName.str.contains("|".join(old))
df["clearance_cat"] = where(df.is_old, df.cat.map(to_clearance_map), "")

# %%
