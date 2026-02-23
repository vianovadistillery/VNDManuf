"""RQ worker: run document generation job and return document_id."""

from __future__ import annotations

import logging
from typing import Any, Dict

from app.adapters.db import get_session
from app.documents.contracts import DocumentOverrides
from app.documents.service import DocumentGenerationService

logger = logging.getLogger(__name__)


def run_document_generation_job(payload: Dict[str, Any]) -> str | None:
    """
    RQ job entrypoint. payload: template_name, doc_type, doc_number, contact_id,
    customer_id, quote_id, delivery_docket_id, line_specs, overrides, output_docx.
    Returns document_id on success; raises on failure (RQ will mark job failed).
    """
    session = get_session()
    try:
        overrides = None
        if payload.get("overrides"):
            o = payload["overrides"]
            from datetime import date
            from decimal import Decimal

            def _date(v):
                if v is None:
                    return None
                if isinstance(v, date):
                    return v
                return date.fromisoformat(str(v)[:10])

            def _decimal(v):
                if v is None:
                    return None
                return Decimal(str(v))

            overrides = DocumentOverrides(
                quote_date=_date(o.get("quote_date")),
                delivery_date=_date(o.get("delivery_date")),
                notes=o.get("notes"),
                shipping=o.get("shipping"),
                payment_terms=o.get("payment_terms"),
                discount_percent=_decimal(o.get("discount_percent")),
            )
        svc = DocumentGenerationService(session)
        doc_record, pdf_path, docx_path, err = svc.generate(
            template_name=payload["template_name"],
            doc_type=payload.get("doc_type", "delivery_docket"),
            doc_number=payload.get("doc_number") or "doc",
            contact_id=payload.get("contact_id"),
            customer_id=payload.get("customer_id"),
            quote_id=payload.get("quote_id"),
            delivery_docket_id=payload.get("delivery_docket_id"),
            line_specs=payload.get("line_specs") or None,
            overrides=overrides,
            output_docx=payload.get("output_docx"),
        )
        if err:
            raise RuntimeError(err)
        return doc_record.id
    finally:
        session.close()
