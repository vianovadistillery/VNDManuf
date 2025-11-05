# app/services/batch_codes.py
"""Batch code generation service - deterministic sequencing per year."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session


class BatchCodeGenerator:
    """
    Service for generating deterministic batch codes.

    Format: B + YY + 0000
    Example: B250001, B250002 (where 25 is year 2025, 0001/0002 are sequential)
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_batch_code(
        self, product_id: Optional[str] = None, site_code: str = "VND"
    ) -> str:
        """
        Generate a deterministic batch code for the current year.

        Args:
            product_id: Product ID (optional, not used in new format but kept for compatibility)
            site_code: Site code (optional, not used in new format but kept for compatibility)

        Returns:
            Batch code in format B + YY + 0000 (e.g., B250001)

        Note:
            The new format uses a global sequence per year, not per product/date.
            Format: B + 2-digit year + 4-digit increment starting from 0001
        """
        # Get current year (2-digit)
        today = datetime.utcnow()
        year_2digit = today.strftime("%y")  # e.g., "25" for 2025

        # Check for existing batches with this year prefix to find the max sequence
        from app.adapters.db.models import Batch

        # Find the highest sequence number for this year
        year_prefix = f"B{year_2digit}"
        existing_batches = (
            self.db.execute(
                select(Batch).where(Batch.batch_code.like(f"{year_prefix}%"))
            )
            .scalars()
            .all()
        )

        # Also check WorkOrder batch codes
        from app.adapters.db.models import WorkOrder

        existing_wo_batch_codes = (
            self.db.execute(
                select(WorkOrder).where(WorkOrder.batch_code.like(f"{year_prefix}%"))
            )
            .scalars()
            .all()
        )

        max_seq = 0
        # Check Batch table
        for batch in existing_batches:
            if batch.batch_code and batch.batch_code.startswith(year_prefix):
                try:
                    # Extract sequence from batch code (last 4 digits)
                    seq_part = batch.batch_code[-4:]
                    seq_num = int(seq_part)
                    max_seq = max(max_seq, seq_num)
                except (ValueError, IndexError):
                    pass

        # Check WorkOrder batch codes
        for wo in existing_wo_batch_codes:
            if wo.batch_code and wo.batch_code.startswith(year_prefix):
                try:
                    # Extract sequence from batch code (last 4 digits)
                    seq_part = wo.batch_code[-4:]
                    seq_num = int(seq_part)
                    max_seq = max(max_seq, seq_num)
                except (ValueError, IndexError):
                    pass

        # Start from max_seq + 1, or 1 if no existing batches
        seq = max_seq + 1

        # Format: B + YY + 0000 (e.g., B250001)
        batch_code = f"B{year_2digit}{seq:04d}"

        return batch_code
