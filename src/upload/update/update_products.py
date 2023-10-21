from time import sleep

from tqdm import tqdm

from src.api.products import update_product
from src.upload.update.update_custom_fields import update_custom_fields
from src.util import LOGS_DIR


def update_products(payloads):
    failed_to_update = []
    if len(payloads) > 0:
        print(f"Updating {len(payloads)} products in BigCommerce...")
        for i, u in tqdm(enumerate(payloads)):
            uid = u.pop("id")
            res = update_product(uid, u)
            update_custom_fields(uid, u)

            if any([r.status_code == 429 for r in res]):
                try:
                    sleep(int(res.headers["X-Rate-Limit-Time-Reset-Ms"]) / 1000)
                except KeyError:
                    sleep(int(res.headers["X-Rate-Limit-Time-Reset-Ms".lower()]) / 1000)
                res = update_product(uid, u)
                update_custom_fields(uid, u)

            status_codes = [r.status_code for r in res]
            alert_codes = [403, 404]
            for alert_code in alert_codes:
                if any([status_code == alert_code for status_code in status_codes]):
                    print(f"{alert_code} for product with id:", uid)
                    print("payload:", u)
            else:
                failed_to_update.append(res)

    if failed_to_update:
        with open(f"{LOGS_DIR}/failed_to_update.log", "w") as ftu_log_file:
            for update_failure_response_group in failed_to_update:
                for update_failure_response in update_failure_response_group:
                    ftu_log_file.write(update_failure_response.text + "\n")
                # new line after each "group"
                ftu_log_file.write("\n")
