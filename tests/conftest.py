from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope="session")
def _test_env():
    os.environ.setdefault("PROMPTLAB_JWT_SECRET", "test-secret")
    db_path = Path(tempfile.gettempdir()) / "promptlab_test.db"
    os.environ.setdefault("PROMPTLAB_DATABASE_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")

    import promptlab.db as db
    import promptlab.settings as settings_mod

    settings_mod.get_settings.cache_clear()
    settings_mod.settings = settings_mod.get_settings()
    db._engine_for.cache_clear()

    from promptlab.db_models import Base

    engine = db.get_engine()
    Base.metadata.create_all(bind=engine)
    yield
    try:
        db_path.unlink(missing_ok=True)
    except Exception:  # noqa: BLE001
        pass
