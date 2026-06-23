"""Embedded OpenAI configuration for Nova University (DAQ-compatible pattern).

Resolution order for API key:
1. config/openai.json → api_key (literal, preferred)
2. config/openai.json → api_key_env → environment lookup (optional)
3. OPENAI_API_KEY environment variable (fallback only)
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any, Dict

from app.settings import settings

CONFIG_DIR = settings.project_root / "config"
CONFIG_PATH = CONFIG_DIR / "openai.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "api_key": "",
    "api_key_env": "",
    "model": "gpt-4o-mini",
    "enabled": True,
    "max_context_articles": 8,
    "max_tokens": 1200,
    "temperature": 0.25,
    "request_timeout_seconds": 60,
}


def _resolve_api_key_from_mapping(mapping: Dict[str, Any]) -> str:
    api_key_literal = (mapping.get("api_key") or "").strip()
    if api_key_literal:
        return api_key_literal

    api_key_env = (mapping.get("api_key_env") or "").strip()
    if api_key_env:
        return os.getenv(api_key_env, "").strip()

    return ""


def load_openai_config() -> Dict[str, Any]:
    """Load merged OpenAI / Nova U LLM config from disk."""
    cfg = deepcopy(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                cfg.update(raw)
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


def save_openai_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """Persist config to config/openai.json (merges with existing)."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    current = load_openai_config()

    for key, value in updates.items():
        if key not in DEFAULT_CONFIG and key != "api_key":
            continue
        if key == "api_key":
            # Blank or masked placeholder → keep existing key
            if value is None:
                continue
            text = str(value).strip()
            if not text or text.startswith("•"):
                continue
            current["api_key"] = text
            continue
        current[key] = value

    # Never write api_key_env unless explicitly provided
    to_write = {k: current[k] for k in DEFAULT_CONFIG if k in current}
    CONFIG_PATH.write_text(
        json.dumps(to_write, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return public_openai_config()


def mask_api_key(api_key: str) -> str:
    if not api_key:
        return ""
    if len(api_key) <= 8:
        return "••••••••"
    return f"{api_key[:7]}…{api_key[-4:]}"


def load_openai_api_key() -> str:
    cfg = load_openai_config()
    key = _resolve_api_key_from_mapping(cfg)
    if key:
        return key
    return os.getenv("OPENAI_API_KEY", "").strip()


def public_openai_config() -> Dict[str, Any]:
    """Config safe for API/UI (key masked)."""
    cfg = load_openai_config()
    key = _resolve_api_key_from_mapping(cfg)
    return {
        "configured": bool(key),
        "enabled": bool(cfg.get("enabled", True)),
        "model": cfg.get("model") or DEFAULT_CONFIG["model"],
        "max_context_articles": int(
            cfg.get("max_context_articles") or DEFAULT_CONFIG["max_context_articles"]
        ),
        "max_tokens": int(cfg.get("max_tokens") or DEFAULT_CONFIG["max_tokens"]),
        "temperature": float(cfg.get("temperature") or DEFAULT_CONFIG["temperature"]),
        "request_timeout_seconds": int(
            cfg.get("request_timeout_seconds")
            or DEFAULT_CONFIG["request_timeout_seconds"]
        ),
        "api_key_masked": mask_api_key(key),
        "config_path": str(CONFIG_PATH),
    }


def get_llm_runtime() -> Dict[str, Any]:
    """Resolved runtime values for LLM calls."""
    cfg = load_openai_config()
    return {
        "api_key": load_openai_api_key(),
        "enabled": bool(cfg.get("enabled", True)),
        "model": cfg.get("model") or DEFAULT_CONFIG["model"],
        "max_context_articles": int(
            cfg.get("max_context_articles") or DEFAULT_CONFIG["max_context_articles"]
        ),
        "max_tokens": int(cfg.get("max_tokens") or DEFAULT_CONFIG["max_tokens"]),
        "temperature": float(cfg.get("temperature") or DEFAULT_CONFIG["temperature"]),
        "request_timeout_seconds": int(
            cfg.get("request_timeout_seconds")
            or DEFAULT_CONFIG["request_timeout_seconds"]
        ),
    }
