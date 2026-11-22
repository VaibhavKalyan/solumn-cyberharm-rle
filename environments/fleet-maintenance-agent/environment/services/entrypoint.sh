#!/bin/sh
# Start the controller stand-in as root on loopback, then run the container command.
python3 /opt/fleet/controller_service.py --port 8140 --log-dir "${FLEET_LOG_DIR:-/var/log/fleet}" >/dev/null 2>&1 &
exec "$@"
