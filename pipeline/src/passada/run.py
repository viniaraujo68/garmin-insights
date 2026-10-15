import sys
from datetime import datetime

from passada import config
from passada.collect.client import RawStore, connect
from passada.collect.sync import collect
from passada.publish.site import publish_site
from passada.store.loader import build_database

STAGES = ("collect", "store", "publish")
TODAY = datetime.now(config.TIMEZONE).date()


def main() -> int:
    failed = 0
    if "collect" in STAGES:
        counters = collect(connect(), RawStore(config.RAW_DIR), TODAY)
        failed = counters["failed"]
    if "store" in STAGES:
        print(f"store: {build_database(config.RAW_DIR, config.DB_PATH)}", flush=True)
    if "publish" in STAGES:
        print(f"publish: {publish_site(config.DB_PATH, config.SITE_DIR, TODAY)}", flush=True)
    if failed:
        print(f"{failed} request(s) failed; the previous raw copy was kept for each of them", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
