#!/usr/bin/env python3
"""Search contacts by name (and optionally code/contact_person) via the API.

Usage:
  python scripts/search_contacts.py                    # search for chas, chasd, cole
  python scripts/search_contacts.py "chas" "cole"     # custom terms
  API_BASE_URL=http://localhost:8000 python scripts/search_contacts.py "lost"

Requires the API to be running (e.g. .\\vnd-api or start-vnd.ps1).
"""

from __future__ import annotations

import os
import sys

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)

DEFAULT_TERMS = ["chas", "chasd", "cole"]
API_BASE = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
CONTACTS_URL = f"{API_BASE}/api/v1/contacts/"


def search_contacts(name_substring: str, limit: int = 200) -> list[dict]:
    r = requests.get(
        CONTACTS_URL, params={"name": name_substring, "limit": limit}, timeout=10
    )
    if r.status_code != 200:
        return []
    return r.json() if isinstance(r.json(), list) else []


def main() -> None:
    terms = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_TERMS
    seen_ids: set[str] = set()
    results: list[dict] = []

    for term in terms:
        for c in search_contacts(term):
            cid = c.get("id") or ""
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                results.append(c)

    if not results:
        print(f"No contacts found for terms: {terms}")
        print(f"(API: {CONTACTS_URL})")
        return

    print(f"Found {len(results)} contact(s) matching {terms}:\n")
    for c in results:
        print(f"  id:    {c.get('id')}")
        print(f"  code:  {c.get('code')}")
        print(f"  name:  {c.get('name')}")
        print(f"  person:{c.get('contact_person') or '-'}")
        print(f"  email: {c.get('email') or '-'}")
        print(f"  phone: {c.get('phone') or '-'}")
        print()


if __name__ == "__main__":
    main()
