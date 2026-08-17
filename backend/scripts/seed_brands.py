from app.core.db import SessionLocal
from app.models import Brand

BRANDS = [
    {"name": "Levi's", "official_domain": "levi.com", "keywords": ["levis", "levi"]},
    {"name": "Levi's (levis.com)", "official_domain": "levis.com", "keywords": []},
    {"name": "Patagonia", "official_domain": "patagonia.com", "keywords": ["patagonia"]},
]

def main() -> None:
    with SessionLocal() as s:
        for b in BRANDS:
            if not s.query(Brand).filter_by(name=b["name"]).first():
                s.add(Brand(**b))
        s.commit()
        print(f"{s.query(Brand).count()} brands in database")

if __name__ == "__main__":
    main()