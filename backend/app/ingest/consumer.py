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

# How often the live consumer reports throughput.
HEARTBEAT_EVERY = 5000


def extract_domains(message: dict) -> list[str]:
    """Pull the SAN list out of a CertStream message, ignoring heartbeats."""
    if message.get("message_type") != "certificate_update":
        return []
    return message.get("data", {}).get("leaf_cert", {}).get("all_domains", []) or []


def handle_message(message: dict, watchlist: Watchlist, session) -> int:
    """Insert any watchlist matches from this message. Returns rows inserted."""
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
    """Yield CertStream messages from a JSONL file."""
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def run_replay(path: Path) -> None:
    """Process a recorded stream. Deterministic, works offline."""
    with SessionLocal() as session:
        watchlist = Watchlist.from_db(session)
        total = sum(handle_message(m, watchlist, session) for m in replay(path))
        session.commit()
        print(f"replay complete: {total} new candidates")


def run_live() -> None:
    """Subscribe to the CertStream firehose and match in real time."""
    import certstream

    session = SessionLocal()
    watchlist = Watchlist.from_db(session)
    log.info(
        "watchlist loaded: %d exact permutations, %d keywords",
        len(watchlist.exact),
        len(watchlist.keywords),
    )

    counter = {"seen": 0, "matched": 0}

    def on_message(message, context):  # noqa: ANN001
        counter["seen"] += 1

        if counter["seen"] % HEARTBEAT_EVERY == 0:
            log.info(
                "processed %d messages, %d matches so far",
                counter["seen"],
                counter["matched"],
            )

        hits = handle_message(message, watchlist, session)
        if hits:
            counter["matched"] += hits
            session.commit()

    def on_error(exc):  # noqa: ANN001
        log.error("certstream error: %s", exc)

    log.info("connecting to %s", settings.certstream_url)
    certstream.listen_for_events(
        on_message, url=settings.certstream_url, on_error=on_error
    )