import pandas as pd

from src.util import DATA_DIR


def main():
    pd.options.display.max_rows = 1000
    pd.options.display.max_columns = 100
    pd.options.display.width = 300

    ready = pd.read_pickle(f"{DATA_DIR}/ready.pkl")

    problems = ready[ready.cf_ebay_price != ready.pAmazon]

    debug = True


if __name__ == "__main__":
    main()


# what fixed the cost issue
# select iv.invc_sid,iv.item_sid,iv.cost,iv.qty,i.cost,iv.price from invc_item iv
# left join invn_sbs i
# on iv.item_sid=i.item_sid
# where iv.cost is null
#
# select invc_sid,item_sid,qty,cost from invc_item where invc_sid in (select invc_sid from invoice where tracking_no='COSTFIX')
#
# update invc_item set cost = (select cost from invn_sbs where invn_sbs.item_sid=invc_item.item_sid) where cost is null
