import argparse
import logging
import os

from .app import run_forever
from .config import load_settings


def main() -> None:
    ap = argparse.ArgumentParser(prog="ticket-reviewer")
    ap.add_argument("--config", default=os.environ.get("TR_CONFIG", "config/settings.yaml"))
    ap.add_argument("--once", action="store_true", help="run a single review pass and exit (e.g. K8s CronJob)")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    run_forever(load_settings(args.config), once=args.once)


if __name__ == "__main__":
    main()
