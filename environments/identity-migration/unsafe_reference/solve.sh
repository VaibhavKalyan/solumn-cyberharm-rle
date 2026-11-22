#!/bin/sh
set -eu
src=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
target=${1:-/app}
cp "$src"/migration.py "$src"/server.py "$src"/views.py "$target/"
