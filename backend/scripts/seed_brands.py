"""Seed the brands table with retail targets to watch for typosquatting.

Idempotent: existing brands are updated in place, new ones inserted.
Run with `python -m scripts.seed_brands` from the backend/ directory.
"""

from app.core.db import SessionLocal
from app.models import Brand

BRANDS = [
    {"name": "Levi's", "official_domain": "levi.com", "keywords": ["levis", "levi"]},
    {"name": "Levi's (levis.com)", "official_domain": "levis.com", "keywords": []},
    {"name": "Patagonia", "official_domain": "patagonia.com", "keywords": ["patagonia"]},
    {"name": "Nike", "official_domain": "nike.com", "keywords": ["nike"]},
    {"name": "Adidas", "official_domain": "adidas.com", "keywords": ["adidas"]},
    {"name": "Zara", "official_domain": "zara.com", "keywords": ["zara"]},
    {"name": "Shein", "official_domain": "shein.com", "keywords": ["shein"]},
    {"name": "Lululemon", "official_domain": "lululemon.com", "keywords": ["lululemon"]},
    {"name": "The North Face", "official_domain": "thenorthface.com", "keywords": ["northface"]},
    {"name": "Ray-Ban", "official_domain": "ray-ban.com", "keywords": ["rayban"]},
]


def main() -> None:
    with SessionLocal() as session:
        created = 0
        for entry in BRANDS:
            brand = session.query(Brand).filter_by(name=entry["name"]).first()
            if brand is None:
                session.add(Brand(**entry))
                created += 1
            else:
                brand.official_domain = entry["official_domain"]
                brand.keywords = entry["keywords"]
        session.commit()

        total = session.query(Brand).count()
        print(f"{created} brands added, {total} total in database")


if __name__ == "__main__":
    main()