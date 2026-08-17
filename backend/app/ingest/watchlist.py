from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.ingest.permutations import permutations_for
from app.models import Brand


@dataclass
class Watchlist:
    exact: dict[str, tuple[int, str]] = field(default_factory=dict)
    keywords: list[tuple[str, int]] = field(default_factory=list)

    @classmethod
    def from_db(cls, session: Session) -> "Watchlist":
        wl = cls()
        for brand in session.query(Brand).all():
            for perm in permutations_for(brand.official_domain):
                wl.exact.setdefault(perm, (brand.id, "permutation"))
            for kw in brand.keywords:
                wl.keywords.append((kw.lower(), brand.id))
        return wl

    def match(self, domain: str) -> tuple[int, str] | None:
        d = domain.lower().lstrip("*.")

        if d in self.exact:
            return self.exact[d]

        label = d.split(".")[0]
        for kw, brand_id in self.keywords:
            if kw in label and label != kw:
                return brand_id, f"keyword:{kw}"
        return None