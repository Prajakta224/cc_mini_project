"""
DEVELOPMENT-ONLY seed script.
Creates two demo accounts and uploads sample files.

WARNING: These credentials are for DEVELOPMENT/DEMO ONLY.
         Remove or change them before any production deployment.

Usage: python -m scripts.seed_demo
"""
import sys
import os

# Ensure the backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load .env
from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.file_record import FileRecord
from app.services.auth_service import hash_password
from app.services.crypto_service import encrypt_file
from app.services.storage.factory import get_storage_provider
from app.services.audit_service import log_event
import secrets
from datetime import datetime, timezone

Base.metadata.create_all(bind=engine)

DEMO_USERS = [
    {"name": "Alice Demo", "email": "alice@afes.demo", "password": "Demo@Alice1", "role": "user"},
    {"name": "Bob Demo", "email": "bob@afes.demo", "password": "Demo@Bob1", "role": "user"},
    {"name": "Admin Demo", "email": "admin@afes.demo", "password": "Demo@Admin1", "role": "admin"},
]

SAMPLE_FILES = {
    "alice@afes.demo": [
        ("sample_report.txt", b"AFES Sample Report\n==================\nThis is a demonstration file encrypted with AES-256-GCM.\nProject: Authenticated File Encryption System\nDate: 2024\n"),
        ("confidential_notes.txt", b"Confidential Meeting Notes\n--------------------------\nDiscussed cloud security best practices.\nAES-256-GCM provides authenticated encryption.\nEnvelope encryption protects per-file keys.\n"),
    ],
    "bob@afes.demo": [
        ("bobs_document.txt", b"Bob's Personal Document\n=======================\nThis file belongs to Bob and cannot be accessed by Alice.\nDemonstrating per-user file isolation in AFES.\n"),
    ],
}


def seed():
    db = SessionLocal()
    storage = get_storage_provider()
    print("\n[SEED] Creating demo users...")

    created_users = {}
    for ud in DEMO_USERS:
        existing = db.query(User).filter(User.email == ud["email"]).first()
        if existing:
            print(f"  [SKIP] {ud['email']} already exists")
            created_users[ud["email"]] = existing
            continue
        user = User(
            name=ud["name"],
            email=ud["email"],
            password_hash=hash_password(ud["password"]),
            role=ud["role"],
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users[ud["email"]] = user
        print(f"  [OK] Created {ud['email']} (role={ud['role']})")

    print("\n[SEED] Uploading sample encrypted files...")
    for email, files in SAMPLE_FILES.items():
        user = created_users.get(email)
        if not user:
            continue
        for filename, content in files:
            existing = db.query(FileRecord).filter(
                FileRecord.owner_id == user.id,
                FileRecord.original_filename == filename,
                FileRecord.status == "active",
            ).first()
            if existing:
                print(f"  [SKIP] {filename} already exists for {email}")
                continue
            try:
                ciphertext, nonce_hex, encrypted_dek_hex = encrypt_file(content, filename, user.id)
                rand = secrets.token_hex(8)
                object_key = f"users/{user.id}/demo_{rand}_{filename}.enc"
                enc_size = storage.upload_object(object_key, ciphertext, "application/octet-stream")
                record = FileRecord(
                    owner_id=user.id,
                    original_filename=filename,
                    original_size=len(content),
                    content_type="text/plain",
                    encrypted_object_key=object_key,
                    encrypted_size=len(ciphertext),
                    encryption_algorithm="AES-256-GCM",
                    format_version=1,
                    nonce_hex=nonce_hex,
                    encrypted_dek_hex=encrypted_dek_hex,
                    storage_provider=storage.provider_name,
                    status="active",
                )
                db.add(record)
                db.commit()
                print(f"  [OK] Encrypted and uploaded '{filename}' for {email}")
            except Exception as e:
                print(f"  [WARN] Could not upload '{filename}' for {email}: {e}")

    print("\n[SEED] Complete!")
    print("\n" + "="*60)
    print("DEMO CREDENTIALS (DEVELOPMENT ONLY — REMOVE BEFORE PRODUCTION)")
    print("="*60)
    for ud in DEMO_USERS:
        print(f"  Email: {ud['email']}  Password: {ud['password']}  Role: {ud['role']}")
    print("="*60 + "\n")
    db.close()


if __name__ == "__main__":
    seed()
