#!/bin/sh
set -eu
python3 /tests/grade.py --repo /app --out /logs/verifier
