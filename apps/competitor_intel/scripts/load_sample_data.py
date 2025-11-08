from __future__ import annotations

from apps.competitor_intel.app.services.db import session_scope
from apps.competitor_intel.app.services.sample_data import load_sample_data


def main() -> None:
    with session_scope() as session:
        summary = load_sample_data(session)
    print("Sample data ready:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
