"""Use OpenAI to suggest Australian retail addresses for customers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

import httpx

from app.services.openai_config import get_llm_runtime

_SYSTEM = """You help locate Australian liquor retail customers (bottle shops, venues, chains).
Given a business name and optional hints, return the best-known street address in Australia.
Respond with JSON only — no markdown. Use null for unknown fields.
Be conservative: if unsure, set confidence below 0.5 and explain in notes."""


@dataclass
class LlmAddressSuggestion:
    line1: Optional[str]
    suburb: Optional[str]
    state: Optional[str]
    postcode: Optional[str]
    country: str
    confidence: float
    notes: Optional[str] = None


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def suggest_customer_address(
    name: str,
    *,
    buying_group: Optional[str] = None,
    suburb: Optional[str] = None,
    state: Optional[str] = None,
    country: str = "Australia",
) -> Optional[LlmAddressSuggestion]:
    """Ask ChatGPT for a structured address; returns None if OpenAI is not configured."""
    cfg = get_llm_runtime()
    if not cfg.get("api_key") or not cfg.get("enabled", True):
        return None

    hints = []
    if buying_group:
        hints.append(f"Buying group / chain: {buying_group}")
    if suburb:
        hints.append(f"Suburb hint: {suburb}")
    if state:
        hints.append(f"State hint: {state}")
    hint_block = "\n".join(hints) if hints else "No extra hints."

    user_msg = (
        f"Business name: {name}\n"
        f"Country: {country}\n"
        f"{hint_block}\n\n"
        "Return JSON:\n"
        '{"line1":"street address","suburb":"","state":"NSW|VIC|...","postcode":"","'
        '"country":"Australia","confidence":0.0,"notes":""}'
    )

    with httpx.Client(timeout=cfg["request_timeout_seconds"]) as client:
        resp = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": cfg["model"],
                "messages": [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                "temperature": 0.2,
                "max_tokens": 400,
                "response_format": {"type": "json_object"},
            },
        )

    if resp.status_code != 200:
        raise ValueError(f"OpenAI error {resp.status_code}: {resp.text[:300]}")

    content = resp.json()["choices"][0]["message"]["content"]
    data = _extract_json(content)
    try:
        confidence = float(data.get("confidence") or 0)
    except (TypeError, ValueError):
        confidence = 0.0

    return LlmAddressSuggestion(
        line1=(data.get("line1") or "").strip() or None,
        suburb=(data.get("suburb") or "").strip() or None,
        state=(data.get("state") or "").strip() or None,
        postcode=str(data.get("postcode") or "").strip() or None,
        country=(data.get("country") or country).strip() or country,
        confidence=confidence,
        notes=(data.get("notes") or "").strip() or None,
    )
