from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

from app.core.config import settings
from app.core.db import SessionLocal
from app.ingest.watchlist import Watchlist
from app.models import Candidate

log = logging.getLogger(__name__)


def extract_domains(message: dict) -> list[str]:
    if message.get("message_type") != "certificate_update":
        return []
    return message.get("data", {}).get("leaf_cert", {}).get("all_domains", []) or []


def handle_message(message: dict, watchlist: Watchlist, session) -> int:
    hits = 0
    for domain in extract_domains(message):
        match = watchlist.match(domain)
        if not match:
            continue
        brand_id, reason = match
        stmt = (
            insert(Candidate)
            .values(
                domain=domain.lower().lstrip("*."),
                brand_id=brand_id,
                source="ct_log",
                match_reason=reason,
            )
            .on_conflict_do_nothing(index_elements=["domain"])
        )
        result = session.execute(stmt)
        if result.rowcount:
            hits += 1
            log.info("MATCH %s (%s)", domain, reason)
    return hits


def replay(path: Path) -> Iterator[dict]:
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def run_replay(path: Path) -> None:
    with SessionLocal() as session:
        watchlist = Watchlist.from_db(session)
        total = sum(handle_message(m, watchlist, session) for m in replay(path))
        session.commit()
        print(f"replay complete: {total} new candidates")


def run_live() -> None:
    import certstream

    session = SessionLocal()
    watchlist = Watchlist.from_db(session)

    def on_message(message, context):  # noqa: ANN001
        if handle_message(message, watchlist, session):
            session.commit()

    def on_error(exc):  # noqa: ANN001
        log.error("certstream error: %s", exc)

    log.info("connecting to %s", settings.certstream_url)
    certstream.listen_for_events(
        on_message, url=settings.certstream_url, on_error=on_error
    )