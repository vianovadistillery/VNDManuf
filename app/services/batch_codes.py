# app/services/batch_codes.py
"""Batch code generation service - deterministic sequencing per product/date."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.db.models import BatchSeq, Product


class BatchCodeGenerator:
    """
    Service for generating deterministic batch codes.

    Format: {SITE}-{PROD}-{YYYYMMDD}-{SEQ}
    Example: VND-GIN42-20251104-03
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_batch_code(self, product_id: str, site_code: str = "VND") -> str:
        """
        Generate a deterministic batch code for a product on the current date.

        Args:
            product_id: Product ID
            site_code: Site code (default: VND)

        Returns:
            Batch code in format {SITE}-{PROD}-{YYYYMMDD}-{SEQ}

        Raises:
            ValueError: If product not found
        """
        # Validate product exists
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Get product code/SKU (use first 6 chars, uppercase)
        prod_code = (product.sku or product.name or "UNK")[:6].upper().replace(" ", "")

        # Get current date string (YYYYMMDD)
        today = datetime.utcnow()
        date_str = today.strftime("%Y%m%d")

        # Get or create sequence entry for this product/date
        seq_entry = self.db.execute(
            select(BatchSeq).where(
                BatchSeq.product_id == product_id, BatchSeq.date == date_str
            )
        ).scalar_one_or_none()

        if seq_entry:
            # Increment sequence
            seq_entry.seq += 1
            seq = seq_entry.seq
        else:
            # Create new sequence entry
            seq_entry = BatchSeq(
                id=str(uuid4()),
                product_id=product_id,
                date=date_str,
                seq=1,
            )
            self.db.add(seq_entry)
            seq = 1

        self.db.flush()

        # Format: VND-GIN42-20251104-03
        batch_code = f"{site_code}-{prod_code}-{date_str}-{seq:02d}"

        return batch_code
