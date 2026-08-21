from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.schemas import BrandOut, CandidateOut, CandidatePage
from app.core.deps import get_db
from app.models import Brand, Candidate, CandidateStatus

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/brands", response_model=list[BrandOut])
def list_brands(db: Session = Depends(get_db)):
    return db.scalars(select(Brand).order_by(Brand.name)).all()


@router.get("/candidates", response_model=CandidatePage)
def list_candidates(
    db: Session = Depends(get_db),
    brand_id: int | None = None,
    status: CandidateStatus | None = None,
    match_reason: str | None = None,
    seen_after: datetime | None = None,
    seen_before: datetime | None = None,
    q: str | None = Query(None, description="Substring match on domain"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> CandidatePage:
    stmt = select(Candidate)

    if brand_id is not None:
        stmt = stmt.where(Candidate.brand_id == brand_id)
    if status is not None:
        stmt = stmt.where(Candidate.status == status)
    if match_reason:
        stmt = stmt.where(Candidate.match_reason.startswith(match_reason))
    if seen_after:
        stmt = stmt.where(Candidate.first_seen_at >= seen_after)
    if seen_before:
        stmt = stmt.where(Candidate.first_seen_at <= seen_before)
    if q:
        stmt = stmt.where(Candidate.domain.ilike(f"%{q}%"))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    rows = db.scalars(
        stmt.order_by(Candidate.first_seen_at.desc()).limit(limit).offset(offset)
    ).all()

    return CandidatePage(items=rows, total=total, limit=limit, offset=offset)


@router.get("/candidates/{candidate_id}", response_model=CandidateOut)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate