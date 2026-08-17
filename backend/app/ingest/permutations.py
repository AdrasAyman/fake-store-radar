"""Generate typosquat permutations for a brand domain."""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)

SUSPICIOUS_TLDS = ["shop", "store", "online", "sale", "outlet", "co", "net", "xyz", "top"]
SUFFIXES = ["outlet", "sale", "clearance", "official", "store", "shop", "us", "uk"]
HOMOGLYPHS = {"l": "1", "i": "1", "o": "0", "e": "3", "a": "@", "s": "5"}


def _fallback(domain: str) -> set[str]:
    base, _, tld = domain.partition(".")
    out: set[str] = set()

    for t in SUSPICIOUS_TLDS:
        out.add(f"{base}.{t}")
    for s in SUFFIXES:
        out.add(f"{base}{s}.{tld}")
        out.add(f"{base}-{s}.{tld}")
        out.add(f"{base}-{s}.shop")
    for i, ch in enumerate(base):
        if ch in HOMOGLYPHS:
            out.add(f"{base[:i]}{HOMOGLYPHS[ch]}{base[i+1:]}.{tld}")
        out.add(f"{base[:i]}{base[i+1:]}.{tld}")          # omission
        out.add(f"{base[:i]}{ch}{ch}{base[i+1:]}.{tld}")  # repetition

    out.discard(domain)
    return out


def permutations_for(domain: str) -> set[str]:
    """Try dnstwist for a rich permutation set; fall back to hand-rolled rules."""
    try:
        import dnstwist

        fuzzer = dnstwist.Fuzzer(domain)
        fuzzer.generate()
        generated = {d["domain"] for d in fuzzer.domains if d.get("domain")}
        generated.discard(domain)
        if generated:
            return generated | _fallback(domain)
    except Exception as exc:  # noqa: BLE001
        log.warning("dnstwist unavailable (%s); using fallback permutations", exc)

    return _fallback(domain)