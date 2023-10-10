import datetime as dt

from src.constants import customer_data


def times(time, regular=True):
    utc = dt.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
    if regular:
        now = utc - dt.timedelta(hours=8)
    else:
        now = utc
    a_second_ago = now - dt.timedelta(seconds=1)
    return {
        "utc": dt.datetime.strftime(utc, "%Y-%m-%dT%H:%M:%S"),
        "now": dt.datetime.strftime(now, "%Y-%m-%dT%H:%M:%S"),
        "a_second_ago": dt.datetime.strftime(a_second_ago, "%Y-%m-%dT%H:%M:%S"),
    }


def invoice_attrib(order, no, invc_sid_top, regular=True):
    diff = abs(
        min(
            0,
            round(
                order["total_amt"] - sum([p["amt_total"] for p in order["products"]]), 2
            ),
        )
    )
    if regular:
        t = times(order["created_date"])
    else:
        t = times(dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), regular=False)
    invoice_attrib = dict(
        # invc_sid = sid(),
        invc_sid=invc_sid_top,
        sbs_no="1",
        invc_no=str(no),
        store_no="1",
        invc_type=("2", "0")[regular],
        # TODO invc_no =
        status="0",
        proc_status="0",
        cust_sid=customer_data[order["payment_zone"]]["sid"],
        addr_no="1",
        workstation="3",
        orig_store_no="1",
        use_vat="0",
        vat_options="0",
        disc_perc=str(round(100 * diff / order["total_amt"], 0)),
        disc_amt=str(diff),
        created_date=t["now"],
        modified_date=t["utc"],
        post_date=t["a_second_ago"],
        audited="0",
        cms_post_date=t["a_second_ago"],
        # TODO ask ken, ws_seq_no???
        held="0",
        controller="1",
        orig_controller="1",
        empl_sbs_no="1",
        empl_name="web",
        createdby_sbs_no="1",
        createdby_empl_name="web",
        # TODO ask ken, elapsed_time???,
        modifiedby_sbs_no="1",
        modifiedby_empl_name="web",
        drawer_no="1",
        activity_percent="100",
        # TODO ask ken, eft_invc_no???
        detax="0",
        clerk_sbs_no="1",
        clerk_name=order["channel"][:8]
        # TODO tracking_no
    )
    return invoice_attrib
