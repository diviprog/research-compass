#!/usr/bin/env python3
"""
Seed a test user into the database for development/testing.
Use this to avoid signing up repeatedly.

Default credentials:
  Email:    test@example.com
  Password: TestPass123

Run from backend directory: python seed_test_user.py
"""

import os
import sys
from pathlib import Path

# Add backend to path so app is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.database import SessionLocal, init_db
from app.models.user import User
from app.core.auth import hash_password

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPass123"  # Meets backend rules: 8+ chars, upper, lower, digit
TEST_NAME = "Test User"
TEST_RESEARCH_INTERESTS = "Machine learning and natural language processing."


def seed_test_user() -> bool:
    """Create or update the test user. Returns True if user was created/updated."""
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == TEST_EMAIL).first()
        if existing:
            existing.password_hash = hash_password(TEST_PASSWORD)
            existing.name = TEST_NAME
            existing.research_interests = TEST_RESEARCH_INTERESTS
            db.commit()
            db.refresh(existing)
            print(f"✓ Test user updated: {TEST_EMAIL}")
            return True
        user = User(
            email=TEST_EMAIL,
            password_hash=hash_password(TEST_PASSWORD),
            name=TEST_NAME,
            research_interests=TEST_RESEARCH_INTERESTS,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✓ Test user created: {TEST_EMAIL}")
        return True
    finally:
        db.close()


if __name__ == "__main__":
    seed_test_user()
    print()
    print("You can sign in with:")
    print(f"  Email:    {TEST_EMAIL}")
    print(f"  Password: {TEST_PASSWORD}")
