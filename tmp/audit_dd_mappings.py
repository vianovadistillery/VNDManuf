import csv
import sys
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.adapters.db import get_session
from app.adapters.db.models import (
    CustomerImportAlias,
    CustomerSite,
    CustomerSiteImportAlias,
)
from apps.vndmanuf_sales.services.customer_mapping import (
    CustomerMappingService,
    names_refer_to_same_entity,
)

path = Path(r"c:\Users\pduxs\Downloads\dd_output.csv")
with path.open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

groups = {}
for r in rows:
    key = (r["customer"].strip(), r["site_name"].strip())
    groups[key] = r

with closing(get_session()) as db:
    svc = CustomerMappingService(db)
    print("CSV customer/site pairs needing action:")
    for (cust_csv, site_csv), r in sorted(groups.items()):
        c = svc.resolve_customer(cust_csv)
        if not c:
            print(f"  MISSING CUSTOMER: {cust_csv!r}")
            continue
        if not site_csv or names_refer_to_same_entity(site_csv, c.name):
            site_note = "omit site"
        else:
            alias = svc.resolve_site_alias(c.id, site_csv)
            site = svc.resolve_site(c, site_csv, allow_create=False)
            site_note = f"alias={alias!r} resolved={site.site_name if site else None}"
        print(f"  {cust_csv!r} -> {c.name!r} | {site_csv!r} | {site_note}")

    print(
        "\nCustomer aliases:",
        db.execute(select(CustomerImportAlias)).scalars().all().__len__(),
    )
    print(
        "Site aliases:",
        db.execute(select(CustomerSiteImportAlias)).scalars().all().__len__(),
    )
    print("Sites:", db.execute(select(CustomerSite)).scalars().all().__len__())
