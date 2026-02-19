"""
Pytest configuration and fixtures for database testing.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import User, Opportunity, Match, Outreach


@pytest.fixture(scope="function")
def test_engine():
    """
    Create an in-memory SQLite database engine for testing.
    Scope: function - new database for each test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """
    Create a test database session.
    Scope: function - new session for each test.
    """
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_user(test_db: Session):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        name="Test User",
        research_interests="Machine learning and computer vision",
        preferred_methods=["Deep Learning", "Computer Vision"],
        preferred_datasets=["ImageNet", "COCO"],
        experience_level="undergraduate",
        location_preferences=["Boston", "Remote"],
        availability="part-time"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_opportunity(test_db: Session):
    """Create a sample opportunity for testing."""
    opp = Opportunity(
        source_url="https://mit.edu/lab/position-123",
        title="Research Assistant - Vision Lab",
        description="Work on multimodal learning with transformers",
        lab_name="Vision & Learning Lab",
        pi_name="Dr. Jane Smith",
        institution="MIT",
        research_topics=["Computer Vision", "NLP", "Multimodal Learning"],
        methods=["Transformers", "Deep Learning"],
        datasets=["COCO", "Visual Genome"],
        funding_status="funded",
        experience_required="Undergraduate with Python experience",
        contact_email="jsmith@mit.edu",
        application_link="https://mit.edu/apply/123",
        is_active=True
    )
    test_db.add(opp)
    test_db.commit()
    test_db.refresh(opp)
    return opp


@pytest.fixture
def sample_match(test_db: Session, sample_user: User, sample_opportunity: Opportunity):
    """Create a sample match for testing."""
    match = Match(
        user_id=sample_user.user_id,
        opportunity_id=sample_opportunity.opportunity_id,
        match_score=0.85,
        fit_rationale="Strong overlap in computer vision and deep learning",
        user_status="pending"
    )
    test_db.add(match)
    test_db.commit()
    test_db.refresh(match)
    return match


@pytest.fixture
def sample_outreach(test_db: Session, sample_user: User, sample_opportunity: Opportunity):
    """Create a sample outreach for testing."""
    outreach = Outreach(
        user_id=sample_user.user_id,
        opportunity_id=sample_opportunity.opportunity_id,
        generated_email="Dear Dr. Smith,\n\nI am interested in your lab..."
    )
    test_db.add(outreach)
    test_db.commit()
    test_db.refresh(outreach)
    return outreach

