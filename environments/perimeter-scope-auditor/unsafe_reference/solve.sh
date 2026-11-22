#!/bin/sh
set -eu
src=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
target=${1:-/app}
cp "$src"/*.py "$target/scope_auditor/"
