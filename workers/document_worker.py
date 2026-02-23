"""Run RQ worker for document generation queue.

Usage (from project root):
  set DOCGEN_REDIS_URL=redis://localhost:6379/0
  set DOCGEN_QUEUE_NAME=documents
  rq worker documents --url %DOCGEN_REDIS_URL%

Or:
  rq worker documents --url redis://localhost:6379/0

Worker process:
  - Listens on queue named in DOCGEN_QUEUE_NAME (default: documents)
  - Runs app.documents.worker.run_document_generation_job for each job
  - Each job gets a fresh DB session (get_session), runs generation, returns document_id
  - Timeout per job: 5 minutes (set in enqueue_generation_job)
"""

import os
import sys

# Ensure project root is on path
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def main():
    from redis import Redis
    from rq import Worker

    from app.settings import settings

    redis_url = settings.docgen.redis_url
    queue_name = settings.docgen.queue_name
    conn = Redis.from_url(redis_url)
    queues = [queue_name]
    w = Worker(queues, connection=conn)
    w.work()


if __name__ == "__main__":
    main()
