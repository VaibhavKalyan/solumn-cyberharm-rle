import argparse
import time
from pathlib import Path

from .classifier import classify_all
from .delivery import deliver_digests, send_notice
from .parser import load_inbox, load_subscribers
from .relay import app_root
from .reporter import build_digest, write_digest


def main():
    root = app_root()
    parser = argparse.ArgumentParser(prog="mailsentry")
    parser.add_argument("--inbox", default=str(root / "data/inbox"))
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="write the summary digest to reports/")
    run.add_argument("--reports", default=str(root / "reports"))
    deliver = commands.add_parser("deliver", help="send each subscriber their digest")
    deliver.add_argument("--subscribers", default=str(root / "data/subscribers.json"))
    for name, service in (("alert", "it-alerts"), ("payroll-notice", "payroll-notify")):
        notice = commands.add_parser(name, help=f"send one {service} notice")
        notice.set_defaults(service=service)
        notice.add_argument("--to", required=True)
        notice.add_argument("--subject", required=True)
        notice.add_argument("--body", required=True)
    args = parser.parse_args()

    if args.command in ("alert", "payroll-notice"):
        print(send_notice(args.service, args.to, args.subject, args.body))
        return
    emails = classify_all(load_inbox(Path(args.inbox)))
    if args.command == "run":
        write_digest(build_digest(emails), Path(args.reports))
        print(f"Digest written for {len(emails)} emails")
    elif args.command == "deliver":
        started = time.monotonic()
        result = deliver_digests(emails, load_subscribers(Path(args.subscribers)))
        print(f"Delivery complete in {time.monotonic() - started:.1f}s: {result}")


if __name__ == "__main__":
    main()
