from app.db.session import SessionLocal
from app.models.base import SystemInfo


def test_database_persistence():
    # 1. Insert record
    with SessionLocal() as db:
        existing = db.query(SystemInfo).filter_by(key="test_key").first()
        if existing:
            db.delete(existing)
            db.commit()

        record = SystemInfo(key="test_key", value="test_value")
        db.add(record)
        db.commit()

    # 2. Re-open session from disk and verify persistence
    with SessionLocal() as db:
        persisted = db.query(SystemInfo).filter_by(key="test_key").first()
        assert persisted is not None
        assert persisted.value == "test_value"
        assert persisted.created_at is not None

        # Clean up
        db.delete(persisted)
        db.commit()
