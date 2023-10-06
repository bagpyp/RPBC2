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


def retry_request_using_response(original_response, max_retries=3, retry_delay=5):
    original_request = original_response.request
    for i in range(max_retries):
        try:
            new_response = requests.request(
                method=original_request.method,
                url=original_request.url,
                headers=original_request.headers,
            )
            if new_response.ok:
                return new_response
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(retry_delay)
    return original_response
