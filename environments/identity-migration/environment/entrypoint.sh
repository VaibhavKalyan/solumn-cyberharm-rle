#!/bin/sh
set -eu
python3 /opt/cedar/provider_service.py --ledger /var/tmp/cedar-provider.jsonl &
exec "$@"
