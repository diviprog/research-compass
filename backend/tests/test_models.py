"""
Tests for SQLAlchemy model creation, validation, and serialization.
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import User, Opportunity, Match, Outreach


class TestUserModel:
    """Tests for User model."""
    
    def test_create_user(self, test_db: Session):
        """Test creating a user with all fields."""
        user = User(
            email="john@example.com",
            name="John Doe",
            research_interests="AI and robotics",
            preferred_methods=["Machine Learning", "Robotics"],
            preferred_datasets=["Custom", "ROS bags"],
            experience_level="graduate",
            location_preferences=["SF", "Remote"],
            availability="full-time"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.user_id is not None
        assert user.email == "john@example.com"
        assert user.name == "John Doe"
        assert user.experience_level == "graduate"
        assert len(user.preferred_methods) == 2
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_to_dict(self, sample_user: User):
        """Test user serialization to dictionary."""
        user_dict = sample_user.to_dict()
        
        assert user_dict["user_id"] == sample_user.user_id
        assert user_dict["email"] == sample_user.email
        assert user_dict["name"] == sample_user.name
        assert isinstance(user_dict["preferred_methods"], list)
        assert isinstance(user_dict["created_at"], str)
    
    def test_user_unique_email(self, test_db: Session, sample_user: User):
        """Test that email must be unique."""
        duplicate_user = User(
            email=sample_user.email,  # Same email
            name="Different Name",
            research_interests="Different interests",
            experience_level="postdoc"
        )
        test_db.add(duplicate_user)
        
        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


class TestOpportunityModel:
    """Tests for Opportunity model."""
    
    def test_create_opportunity(self, test_db: Session):
        """Test creating an opportunity with all fields."""
        opp = Opportunity(
            source_url="https://stanford.edu/ai-lab/pos-456",
            title="PhD Position - AI Lab",
            description="Looking for PhD students interested in reinforcement learning",
            lab_name="Stanford AI Lab",
            pi_name="Dr. John Doe",
            institution="Stanford University",
            research_topics=["Reinforcement Learning", "AI Safety"],
            methods=["Policy Gradient", "Model-Based RL"],
            datasets=["MuJoCo", "OpenAI Gym"],
            funding_status="funded",
            experience_required="Master's degree required",
            contact_email="jdoe@stanford.edu",
            application_link="https://stanford.edu/apply/456",
            is_active=True
        )
        test_db.add(opp)
        test_db.commit()
        test_db.refresh(opp)
        
        assert opp.opportunity_id is not None
        assert opp.title == "PhD Position - AI Lab"
        assert opp.institution == "Stanford University"
        assert len(opp.research_topics) == 2
        assert opp.is_active is True
        assert opp.scraped_at is not None
    
    def test_opportunity_to_dict(self, sample_opportunity: Opportunity):
        """Test opportunity serialization to dictionary."""
        opp_dict = sample_opportunity.to_dict()
        
        assert opp_dict["opportunity_id"] == sample_opportunity.opportunity_id
        assert opp_dict["title"] == sample_opportunity.title
        assert opp_dict["lab_name"] == sample_opportunity.lab_name
        assert isinstance(opp_dict["research_topics"], list)
        assert isinstance(opp_dict["scraped_at"], str)
    
    def test_opportunity_unique_url(self, test_db: Session, sample_opportunity: Opportunity):
        """Test that source_url must be unique."""
        duplicate_opp = Opportunity(
            source_url=sample_opportunity.source_url,  # Same URL
            title="Different Title",
            description="Different description",
            lab_name="Different Lab",
            pi_name="Different PI",
            institution="Different Institution",
            is_active=True
        )
        test_db.add(duplicate_opp)
        
        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


class TestMatchModel:
    """Tests for Match model."""
    
    def test_create_match(self, test_db: Session, sample_user: User, sample_opportunity: Opportunity):
        """Test creating a match."""
        match = Match(
            user_id=sample_user.user_id,
            opportunity_id=sample_opportunity.opportunity_id,
            match_score=0.92,
            fit_rationale="Excellent match based on research interests",
            user_status="saved"
        )
        test_db.add(match)
        test_db.commit()
        test_db.refresh(match)
        
        assert match.match_id is not None
        assert match.user_id == sample_user.user_id
        assert match.opportunity_id == sample_opportunity.opportunity_id
        assert match.match_score == 0.92
        assert match.user_status == "saved"
        assert match.created_at is not None
    
    def test_match_to_dict(self, sample_match: Match):
        """Test match serialization to dictionary."""
        match_dict = sample_match.to_dict()
        
        assert match_dict["match_id"] == sample_match.match_id
        assert match_dict["user_id"] == sample_match.user_id
        assert match_dict["opportunity_id"] == sample_match.opportunity_id
        assert match_dict["match_score"] == round(sample_match.match_score, 3)
        assert isinstance(match_dict["created_at"], str)
    
    def test_match_score_range(self, test_db: Session, sample_user: User, sample_opportunity: Opportunity):
        """Test that match score is stored correctly."""
        match = Match(
            user_id=sample_user.user_id,
            opportunity_id=sample_opportunity.opportunity_id,
            match_score=0.0,
            user_status="dismissed"
        )
        test_db.add(match)
        test_db.commit()
        
        assert match.match_score == 0.0


class TestOutreachModel:
    """Tests for Outreach model."""
    
    def test_create_outreach(self, test_db: Session, sample_user: User, sample_opportunity: Opportunity):
        """Test creating an outreach."""
        outreach = Outreach(
            user_id=sample_user.user_id,
            opportunity_id=sample_opportunity.opportunity_id,
            generated_email="Dear Professor,\n\nI am writing to express my interest...",
            user_edited_email="Dear Prof. Smith,\n\nI am excited to apply...",
            response_received=False
        )
        test_db.add(outreach)
        test_db.commit()
        test_db.refresh(outreach)
        
        assert outreach.outreach_id is not None
        assert outreach.user_id == sample_user.user_id
        assert outreach.opportunity_id == sample_opportunity.opportunity_id
        assert outreach.generated_email is not None
        assert outreach.user_edited_email is not None
        assert outreach.response_received is False
        assert outreach.sent_at is None
        assert outreach.created_at is not None
    
    def test_outreach_to_dict(self, sample_outreach: Outreach):
        """Test outreach serialization to dictionary."""
        outreach_dict = sample_outreach.to_dict()
        
        assert outreach_dict["outreach_id"] == sample_outreach.outreach_id
        assert outreach_dict["user_id"] == sample_outreach.user_id
        assert outreach_dict["generated_email"] == sample_outreach.generated_email
        assert outreach_dict["response_received"] is False
        assert isinstance(outreach_dict["created_at"], str)

