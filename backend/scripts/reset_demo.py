"""
DEVELOPMENT-ONLY demo reset script.
Deletes ONLY demo@afes.demo accounts and their files.
Never touches production data.

Usage: python -m scripts.reset_demo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()

DEMO_EMAILS = ["alice@afes.demo", "bob@afes.demo", "admin@afes.demo"]

from app.database import SessionLocal, engine
from app.models.user import User
from app.models.file_record import FileRecord
from app.models.audit_event import AuditEvent
from app.services.storage.factory import get_storage_provider


def reset():
    db = SessionLocal()
    storage = get_storage_provider()
    print("\n[RESET] Cleaning demo data...")

    for email in DEMO_EMAILS:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"  [SKIP] {email} not found")
            continue

        # Delete cloud objects
        files = db.query(FileRecord).filter(FileRecord.owner_id == user.id).all()
        for f in files:
            try:
                storage.delete_object(f.encrypted_object_key)
                print(f"  [DEL] Deleted cloud object: {f.encrypted_object_key}")
            except Exception as e:
                print(f"  [WARN] Could not delete object {f.encrypted_object_key}: {e}")
            db.delete(f)

        # Delete audit events
        db.query(AuditEvent).filter(AuditEvent.user_id == user.id).delete()

        # Delete user
        db.delete(user)
        db.commit()
        print(f"  [DEL] Deleted user: {email}")

    print("[RESET] Demo data cleaned.\n")
    db.close()


if __name__ == "__main__":
    reset()
