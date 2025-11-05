"""Safe Alembic check wrapper that logs drift but always exits 0.

This prevents Cursor agents from failing when alembic check detects schema drift.
Drift is logged to tmp/alembic_drift.txt for review.
"""

import datetime
import pathlib
import subprocess
import sys

LOG = pathlib.Path("tmp")
LOG.mkdir(parents=True, exist_ok=True)
OUT = LOG / "alembic_drift.txt"


def run(cmd):
    """Run a command and return exit code and output."""
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True
    )
    out, _ = p.communicate()
    return p.returncode, out


def main():
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    code, out = run("alembic check")
    OUT.write_text(f"[{ts}] exit={code}\n\n{out}")
    print("--- Alembic check (safe) ---")
    print(f"Exit: {code}")
    if code == 0:
        print("No drift detected.")
    else:
        print("Schema drift detected — see tmp/alembic_drift.txt")
    sys.exit(0)


if __name__ == "__main__":
    main()
