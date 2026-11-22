#!/bin/sh
# Start the asset stand-ins as root on loopback, then run the container command.
python3 /opt/assets/assets_service.py --log-dir "${ASSETS_LOG_DIR:-/var/log/assets}" >/dev/null 2>&1 &
exec "$@"
