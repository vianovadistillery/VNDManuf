"""RQ job enqueue and status for async document generation."""

from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_redis_url: Optional[str] = None
_queue_name: str = "documents"


def _get_redis_url() -> str:
    from app.settings import settings

    return settings.docgen.redis_url


def _get_queue_name() -> str:
    from app.settings import settings

    return settings.docgen.queue_name


def enqueue_generation_job(
    template_name: str,
    doc_type: str,
    doc_number: Optional[str] = None,
    contact_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    quote_id: Optional[str] = None,
    delivery_docket_id: Optional[str] = None,
    line_specs: Optional[list[dict]] = None,
    overrides: Optional[dict] = None,
    output_docx: Optional[bool] = None,
) -> str:
    """Enqueue a document generation job. Returns RQ job id."""
    try:
        from redis import Redis
        from rq import Queue
    except ImportError as e:
        logger.warning("RQ not available: %s", e)
        raise RuntimeError(
            "RQ and redis are required for async document generation"
        ) from e

    from app.settings import settings

    redis_url = settings.docgen.redis_url
    queue_name = settings.docgen.queue_name

    payload = {
        "template_name": template_name,
        "doc_type": doc_type,
        "doc_number": doc_number,
        "contact_id": contact_id,
        "customer_id": customer_id,
        "quote_id": quote_id,
        "delivery_docket_id": delivery_docket_id,
        "line_specs": line_specs or [],
        "overrides": overrides,
        "output_docx": output_docx,
    }
    conn = Redis.from_url(redis_url)
    queue = Queue(name=queue_name, connection=conn)
    job = queue.enqueue(
        "app.documents.worker.run_document_generation_job",
        payload,
        job_timeout="5m",
        failure_ttl=86400,
        result_ttl=86400,
    )
    return job.id


def get_job_status(
    job_id: str, db: Optional[Session] = None
) -> Optional[dict[str, Any]]:
    """Return dict with keys: job_id, status (queued|started|finished|failed), document_id, error_message."""
    try:
        from redis import Redis
        from rq.job import Job
    except ImportError:
        return None

    from app.settings import settings

    redis_url = settings.docgen.redis_url

    conn = Redis.from_url(redis_url)
    try:
        job = Job.fetch(job_id, connection=conn)
    except Exception:
        return None

    status_map = {
        "queued": "queued",
        "started": "started",
        "finished": "finished",
        "failed": "failed",
        "deferred": "queued",
        "canceled": "failed",
    }
    rq_status = job.get_status()
    status = status_map.get(rq_status, rq_status)
    out = {
        "job_id": job_id,
        "status": status,
        "document_id": None,
        "error_message": None,
    }
    if job.is_finished and job.result:
        out["document_id"] = job.result
    if job.is_failed:
        out["error_message"] = str(job.exc_info) if job.exc_info else "Job failed"
    return out
