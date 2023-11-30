import datetime as dt

from tqdm import tqdm

from config import apply_changes
from src.api.products import update_product, delete_product
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

            # TODO: move this handling up the stack to `update_product`
            status_codes = [r.status_code for r in res]
            alert_codes = [403, 404]
            for alert_code in alert_codes:
                if alert_code in status_codes:
                    print(f"{alert_code} for product with id:", uid)
                    print("payload:", u)
                    failed_to_update.append(res)
            if apply_changes and any([ac == 404 for ac in status_codes]):
                # delete any product who is missing a variant
                delete_product(uid)

    if failed_to_update:
        with open(f"{LOGS_DIR}/failed_to_update.log", "w") as ftu_log_file:
            ftu_log_file.write(str(dt.datetime.now()) + "\n\n")
            for update_failure_response_group in failed_to_update:
                for update_failure_response in update_failure_response_group:
                    ftu_log_file.write(update_failure_response.text + "\n")
                # new line after each "group"
                ftu_log_file.write("\n")
