"""
Database configuration and session management.
Supports both PostgreSQL (production/development) and SQLite (fallback).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os
from pathlib import Path

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = os.getenv("DATABASE_URL")

# Determine database configuration
if DATABASE_URL is None:
    # Fallback to SQLite for local development
    DATABASE_DIR = Path(__file__).parent.parent.parent / "data"
    DATABASE_DIR.mkdir(exist_ok=True)
    DATABASE_PATH = DATABASE_DIR / "research_compass.db"
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
    print(f"📁 Using SQLite: {DATABASE_PATH}")
else:
    # PostgreSQL configuration
    # Render uses postgres:// but SQLAlchemy requires postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    db_host = DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'localhost'
    print(f"🐘 Using PostgreSQL: {db_host}")

# Create database engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,
        max_overflow=10,
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.

    Core tables (User, Opportunity, Match, Outreach, RefreshToken) are always created.
    On PostgreSQL, embedding tables (user_embeddings, opportunity_embeddings) are
    created only if pgvector is available; otherwise a warning is logged and startup continues.
    """
    from app.db.base import Base
    from app.models.user import User
    from app.models.opportunity import Opportunity
    from app.models.match import Match
    from app.models.outreach import Outreach
    from app.models.refresh_token import RefreshToken

    # Core tables only (no pgvector Vector types)
    core_tables = [
        User.__table__,
        Opportunity.__table__,
        Match.__table__,
        Outreach.__table__,
        RefreshToken.__table__,
    ]
    Base.metadata.create_all(bind=engine, tables=core_tables)
    print("✓ Database initialized (core tables)")

    # On PostgreSQL, try to create embedding tables (require pgvector extension)
    if engine.dialect.name == "postgresql":
        try:
            from app.models.user_embedding import UserEmbedding
            from app.models.opportunity_embedding import OpportunityEmbedding
            Base.metadata.create_all(
                bind=engine,
                tables=[UserEmbedding.__table__, OpportunityEmbedding.__table__],
            )
            print("✓ Embedding tables (user_embeddings, opportunity_embeddings) created")
        except Exception as e:
            print(
                "⚠ Embedding tables skipped (pgvector may not be installed or enabled):",
                str(e),
            )


def reset_db() -> None:
    """
    Drop all tables and recreate them.
    
    WARNING: This will delete all data!
    Use only for development/testing.
    """
    from app.db.base import Base
    from app.models import User, Opportunity, Match, Outreach
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database reset")

