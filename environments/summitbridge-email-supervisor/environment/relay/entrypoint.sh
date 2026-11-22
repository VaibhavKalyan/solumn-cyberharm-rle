#!/bin/sh
# Start the relay stand-in as root on loopback, then hand off to the container command.
python3 /opt/relay/relay_service.py --port 8125 --log-dir "${RELAY_LOG_DIR:-/var/log/relay}" >/dev/null 2>&1 &
exec "$@"
