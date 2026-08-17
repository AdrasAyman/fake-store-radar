import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CandidateStatus(str, enum.Enum):
    pending = "pending"
    crawled = "crawled"
    scored = "scored"
    dismissed = "dismissed"


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id"), nullable=True)
    source: Mapped[str] = mapped_column(String(40), default="ct_log")
    match_reason: Mapped[str] = mapped_column(String(60), default="unknown")
    status: Mapped[CandidateStatus] = mapped_column(
        Enum(CandidateStatus, name="candidate_status"),
        default=CandidateStatus.pending,
        index=True,
    )
    risk_score: Mapped[int | None] = mapped_column(nullable=True)
    evidence: Mapped[dict] = mapped_column(JSONB, default=dict)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


Index("ix_candidates_status_first_seen", Candidate.status, Candidate.first_seen_at)