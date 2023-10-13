import time

import requests


def call_iteratively(call, *args):
    res = call(*args)
    if res.status_code == 429:
        s = int(res.headers["X-Rate-Limit-Time-Reset-Ms"]) / 1000
        time.sleep(s)
        retry_request_using_response(res)
    elif res.ok:
        j = res.json()
        data = j["data"]
        pagination_data = j["meta"]["pagination"]
        for i in range(2, pagination_data["total_pages"] + 1):
            next_request = call(*args, i)
            if next_request.ok:
                data.extend(next_request.json()["data"])
        return data


def retry_request_using_response(original_response, max_retries=2, retry_delay=0.1):
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
