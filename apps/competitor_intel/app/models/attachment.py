from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .price_observation import PriceObservation


class Attachment(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "attachments"

    price_observation_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("price_observations.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(sa.String(1024), nullable=False)
    caption: Mapped[str | None] = mapped_column(sa.String(255))

    price_observation: Mapped["PriceObservation"] = relationship(
        "PriceObservation", back_populates="attachments"
    )
