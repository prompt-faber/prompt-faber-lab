from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from promptlab.db_models import User
from promptlab.security import hash_password


def seed_admin(db: Session) -> None:
    existing = db.query(User).filter(User.email == "admin@promptlab.local").first()
    if existing:
        return
    db.add(
        User(
            id=str(uuid.uuid4()),
            email="admin@promptlab.local",
            password_hash=hash_password("admin123"),
            is_active=True,
        )
    )
    db.commit()
