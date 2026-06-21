import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apps.vndmanuf_sales.services.customer_mapping import (
    name_token_set,
    names_refer_to_same_entity,
)

for site in ["MURPHY'S GEELONG", "MURPHY'S – GEELONG", "Murphy's Geelong"]:
    print(site, name_token_set(site), names_refer_to_same_entity(site, "Murphy's"))
