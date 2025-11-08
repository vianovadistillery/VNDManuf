from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)


@dataclass(frozen=True)
class AppConfig:
    host: str = os.getenv("COMPINTEL_APP_HOST", "127.0.0.1")
    port: int = int(os.getenv("COMPINTEL_APP_PORT", "8060"))
    debug: bool = os.getenv("COMPINTEL_DEBUG", "false").lower() == "true"
    database_url: str = os.getenv(
        "COMPINTEL_DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'competitor_intel.db').as_posix()}",
    )
    evidence_root: Path = Path(
        os.getenv("COMPINTEL_EVIDENCE_ROOT", BASE_DIR / "evidence")
    )
    default_gst_rate: float = float(os.getenv("COMPINTEL_DEFAULT_GST_RATE", "0.10"))
    default_currency: str = os.getenv("COMPINTEL_DEFAULT_CURRENCY", "AUD")
    map_enabled: bool = os.getenv("COMPINTEL_SMAP_ENABLED", "false").lower() == "true"
    requests_pathname_prefix: Optional[str] = os.getenv(
        "COMPINTEL_REQUESTS_PATHNAME_PREFIX"
    )


CONFIG = AppConfig()


__all__ = ["AppConfig", "CONFIG", "BASE_DIR"]
