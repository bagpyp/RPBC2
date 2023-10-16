from time import sleep

from tqdm import tqdm

from src.api.products import update_product, update_custom_field
from src.util import LOGS_DIR


def update_products(payloads):
    updated = []
    failed_to_update = []
    if len(payloads) > 0:
        print(f"Updating {len(payloads)} products in BigCommerce...")
        sleep(1)
        for i, u in tqdm(enumerate(payloads)):
            uid = u.pop("id")

            res = update_product(uid, u)
            update_custom_field(uid, "eBay Sale Price", u["amazon_price"])
            if u["list_on_amazon"]:
                update_custom_field(uid, "Amazon Status", "Enabled")
            else:
                update_custom_field(uid, "Amazon Status", "Disabled")

            if all([r.ok for r in res]):
                updated.append(res)
            elif any([r.status_code == 429 for r in res]):
                sleep(30)
                res = update_product(uid, u, slow=True)
                update_custom_field(uid, "eBay Sale Price", u["amazon_price"])
                if u["list_on_amazon"]:
                    update_custom_field(uid, "Amazon Status", "Enabled")
                else:
                    update_custom_field(uid, "Amazon Status", "Disabled")
                if all([r.ok for r in res]):
                    updated.append(res)
            else:
                failed_to_update.append(res)

    if failed_to_update:
        with open(f"{LOGS_DIR}/failed_to_update.log", "w") as ftu_log_file:
            for update_failure_response_group in failed_to_update:
                for update_failure_response in update_failure_response_group:
                    ftu_log_file.write(update_failure_response.text + "\n")
