#!/usr/bin/env python3
"""Restore all inactive (soft-deleted) sales orders as active.

Calls the API to list orders with include_deleted=True, then POST restore for each
order that has deleted_at set. Run with the API base URL if not using default.

Usage:
  python scripts/restore_all_orders.py [--base-url http://127.0.0.1:8000] [--dry-run]
"""

import argparse
import sys

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Restore all inactive sales orders as active."
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="API base URL (default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Only list orders that would be restored"
    )
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    prefix = f"{base}/api/v1"

    # List all orders including deleted
    resp = requests.get(
        f"{prefix}/sales/orders", params={"include_deleted": True}, timeout=30
    )
    if resp.status_code != 200:
        print(
            f"Failed to list orders: {resp.status_code} {resp.text[:200]}",
            file=sys.stderr,
        )
        sys.exit(1)
    orders = resp.json() if isinstance(resp.json(), list) else []
    inactive = [o for o in orders if o.get("deleted_at")]
    if not inactive:
        print("No inactive orders found.")
        return
    print(f"Found {len(inactive)} inactive order(s) to restore.")
    if args.dry_run:
        for o in inactive:
            ref = o.get("order_ref") or o.get("id", "")[:8]
            print(f"  Would restore: {ref} (id={o.get('id')})")
        return

    restored = 0
    for o in inactive:
        order_id = o.get("id")
        ref = o.get("order_ref") or order_id[:8]
        r = requests.post(f"{prefix}/sales/orders/{order_id}/restore", timeout=30)
        if r.status_code in (200, 201):
            restored += 1
            print(f"  Restored: {ref}")
        else:
            print(f"  Failed {ref}: {r.status_code} {r.text[:100]}", file=sys.stderr)
    print(f"Restored {restored} order(s).")


if __name__ == "__main__":
    main()
