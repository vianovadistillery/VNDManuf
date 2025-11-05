#!/usr/bin/env bash
# Safe migration runner for Unix (Linux/macOS)
# Runs alembic upgrade head and safe check, always exits 0

set -euo pipefail

echo "== alembic upgrade head =="
alembic upgrade head

echo ""
echo "== alembic check (safe) =="
python scripts/alembic_check_safe.py

echo ""
echo "== summary =="
if grep -Eq 'New upgrade operations detected|Detected ' tmp/alembic_drift.txt 2>/dev/null; then
    echo "Drift found → tmp/alembic_drift.txt"
else
    echo "No drift detected."
fi

exit 0
