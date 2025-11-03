import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.golden.print_normalizer import normalize_legacy_print

# Mark as xfail until renderer is implemented
# pytestmark = pytest.mark.xfail(reason="Renderer not implemented yet", strict=False)


def test_batch_ticket_golden():
    legacy = Path("fixtures/print/B060149.PRN").read_bytes().decode("cp437", "ignore")
    exp = normalize_legacy_print(legacy)
    # Import here to avoid hard dependency if module moves
    from app.reports.batch_ticket import generate_batch_ticket_text

    act = normalize_legacy_print(generate_batch_ticket_text(batch_code="B060149"))
    assert act == exp
