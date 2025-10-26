
import pytest
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.golden.print_normalizer import normalize_legacy_print

# pytestmark = pytest.mark.xfail(reason="Renderer not implemented yet", strict=False)

def test_invoice_golden():
    legacy = Path("fixtures/print/00086633.INS").read_bytes().decode("cp437", "ignore")
    exp = normalize_legacy_print(legacy)
    from app.reports.invoice import generate_invoice_text
    act = normalize_legacy_print(generate_invoice_text(invoice_code="00086633"))
    assert act == exp
