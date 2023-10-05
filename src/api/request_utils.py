import time

import requests
from tqdm import tqdm


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
        for i in tqdm(range(2, pag["total_pages"] + 1)):
            subres = call(*args, i)
            if subres.ok:
                data.extend(subres.json()["data"])
        return data


def retry_request_using_response(res):
    r = res.request
    res = requests.request(method=r.method, url=r.url, headers=r.headers)
    return res
