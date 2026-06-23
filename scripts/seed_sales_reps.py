"""Seed default Vianova sales reps."""

from sqlalchemy import select

from app.adapters.db import get_session
from app.adapters.db.models import SalesRep

SEEDS = [
    ("EW", "Emily Withers", "emily@vianova.com.au", None),
    ("PD", "Peter Duxson", "pduxson@vianova.com.au", None),
    ("JT", "Josh Torney", "jtorney@vianova.com.au", None),
]


def main() -> None:
    session = get_session()
    try:
        for code, name, email, phone in SEEDS:
            existing = session.execute(
                select(SalesRep).where(
                    SalesRep.deleted_at.is_(None),
                    (SalesRep.code == code) | (SalesRep.email == email),
                )
            ).scalar_one_or_none()
            if existing:
                existing.name = name
                existing.email = email
                if phone:
                    existing.phone = phone
                existing.is_active = True
                print(f"Updated rep: {name}")
            else:
                session.add(
                    SalesRep(
                        code=code,
                        name=name,
                        email=email,
                        phone=phone,
                        is_active=True,
                    )
                )
                print(f"Added rep: {name}")
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()
