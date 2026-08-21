from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import CandidateStatus


class BrandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    official_domain: str
    keywords: list[str]


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    domain: str
    brand_id: int | None
    source: str
    match_reason: str
    status: CandidateStatus
    risk_score: int | None
    evidence: dict
    first_seen_at: datetime


class CandidatePage(BaseModel):
    items: list[CandidateOut]
    total: int
    limit: int
    offset: int