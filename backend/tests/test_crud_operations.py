"""
Tests for CRUD (Create, Read, Update, Delete) operations on all models.
"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models import User, Opportunity, Match, Outreach


class TestUserCRUD:
    """CRUD tests for User model."""
    
    def test_read_user(self, test_db: Session, sample_user: User):
        """Test reading a user by ID."""
        user = test_db.query(User).filter(User.user_id == sample_user.user_id).first()
        assert user is not None
        assert user.email == sample_user.email
    
    def test_read_user_by_email(self, test_db: Session, sample_user: User):
        """Test querying user by email."""
        user = test_db.query(User).filter(User.email == "test@example.com").first()
        assert user is not None
        assert user.user_id == sample_user.user_id
    
    def test_update_user(self, test_db: Session, sample_user: User):
        """Test updating user fields."""
        sample_user.name = "Updated Name"
        sample_user.experience_level = "graduate"
        test_db.commit()
        test_db.refresh(sample_user)
        
        assert sample_user.name == "Updated Name"
        assert sample_user.experience_level == "graduate"
    
    def test_delete_user(self, test_db: Session, sample_user: User):
        """Test deleting a user."""
        user_id = sample_user.user_id
        test_db.delete(sample_user)
        test_db.commit()
        
        deleted_user = test_db.query(User).filter(User.user_id == user_id).first()
        assert deleted_user is None
    
    def test_list_users(self, test_db: Session):
        """Test listing multiple users."""
        users = [
            User(email=f"user{i}@example.com", name=f"User {i}", 
                 research_interests="AI", experience_level="undergraduate")
            for i in range(5)
        ]
        test_db.add_all(users)
        test_db.commit()
        
        all_users = test_db.query(User).all()
        assert len(all_users) == 5


class TestOpportunityCRUD:
    """CRUD tests for Opportunity model."""
    
    def test_read_opportunity(self, test_db: Session, sample_opportunity: Opportunity):
        """Test reading an opportunity by ID."""
        opp = test_db.query(Opportunity).filter(
            Opportunity.opportunity_id == sample_opportunity.opportunity_id
        ).first()
        assert opp is not None
        assert opp.title == sample_opportunity.title
    
    def test_query_opportunities_by_institution(self, test_db: Session, sample_opportunity: Opportunity):
        """Test querying opportunities by institution."""
        opps = test_db.query(Opportunity).filter(Opportunity.institution == "MIT").all()
        assert len(opps) == 1
        assert opps[0].opportunity_id == sample_opportunity.opportunity_id
    
    def test_update_opportunity(self, test_db: Session, sample_opportunity: Opportunity):
        """Test updating opportunity fields."""
        sample_opportunity.is_active = False
        sample_opportunity.title = "Updated Title"
        test_db.commit()
        test_db.refresh(sample_opportunity)
        
        assert sample_opportunity.is_active is False
        assert sample_opportunity.title == "Updated Title"
    
    def test_delete_opportunity(self, test_db: Session, sample_opportunity: Opportunity):
        """Test deleting an opportunity."""
        opp_id = sample_opportunity.opportunity_id
        test_db.delete(sample_opportunity)
        test_db.commit()
        
        deleted_opp = test_db.query(Opportunity).filter(
            Opportunity.opportunity_id == opp_id
        ).first()
        assert deleted_opp is None
    
    def test_filter_active_opportunities(self, test_db: Session):
        """Test filtering opportunities by active status."""
        # Create mix of active and inactive opportunities
        for i in range(3):
            opp = Opportunity(
                source_url=f"https://example.com/opp-{i}",
                title=f"Opportunity {i}",
                description="Test",
                lab_name="Test Lab",
                pi_name="Dr. Test",
                institution="Test U",
                is_active=(i % 2 == 0)  # Alternate active/inactive
            )
            test_db.add(opp)
        test_db.commit()
        
        active_opps = test_db.query(Opportunity).filter(Opportunity.is_active == True).all()
        assert len(active_opps) == 2  # 0 and 2 are active


class TestMatchCRUD:
    """CRUD tests for Match model."""
    
    def test_read_match(self, test_db: Session, sample_match: Match):
        """Test reading a match by ID."""
        match = test_db.query(Match).filter(Match.match_id == sample_match.match_id).first()
        assert match is not None
        assert match.match_score == sample_match.match_score
    
    def test_query_matches_by_user(self, test_db: Session, sample_match: Match):
        """Test querying matches for a specific user."""
        matches = test_db.query(Match).filter(Match.user_id == sample_match.user_id).all()
        assert len(matches) == 1
        assert matches[0].match_id == sample_match.match_id
    
    def test_update_match_status(self, test_db: Session, sample_match: Match):
        """Test updating match status."""
        sample_match.user_status = "contacted"
        test_db.commit()
        test_db.refresh(sample_match)
        
        assert sample_match.user_status == "contacted"
    
    def test_delete_match(self, test_db: Session, sample_match: Match):
        """Test deleting a match."""
        match_id = sample_match.match_id
        test_db.delete(sample_match)
        test_db.commit()
        
        deleted_match = test_db.query(Match).filter(Match.match_id == match_id).first()
        assert deleted_match is None
    
    def test_filter_matches_by_score(self, test_db: Session, sample_user: User, sample_opportunity: Opportunity):
        """Test filtering matches by minimum score."""
        # Create matches with different scores
        scores = [0.9, 0.7, 0.5, 0.3]
        for score in scores:
            match = Match(
                user_id=sample_user.user_id,
                opportunity_id=sample_opportunity.opportunity_id,
                match_score=score,
                user_status="pending"
            )
            test_db.add(match)
        test_db.commit()
        
        high_matches = test_db.query(Match).filter(Match.match_score >= 0.7).all()
        assert len(high_matches) == 2


class TestOutreachCRUD:
    """CRUD tests for Outreach model."""
    
    def test_read_outreach(self, test_db: Session, sample_outreach: Outreach):
        """Test reading an outreach by ID."""
        outreach = test_db.query(Outreach).filter(
            Outreach.outreach_id == sample_outreach.outreach_id
        ).first()
        assert outreach is not None
        assert outreach.generated_email == sample_outreach.generated_email
    
    def test_update_outreach_email(self, test_db: Session, sample_outreach: Outreach):
        """Test updating outreach email."""
        sample_outreach.user_edited_email = "Updated email content"
        sample_outreach.sent_at = datetime.utcnow()
        test_db.commit()
        test_db.refresh(sample_outreach)
        
        assert sample_outreach.user_edited_email == "Updated email content"
        assert sample_outreach.sent_at is not None
    
    def test_delete_outreach(self, test_db: Session, sample_outreach: Outreach):
        """Test deleting an outreach."""
        outreach_id = sample_outreach.outreach_id
        test_db.delete(sample_outreach)
        test_db.commit()
        
        deleted_outreach = test_db.query(Outreach).filter(
            Outreach.outreach_id == outreach_id
        ).first()
        assert deleted_outreach is None
    
    def test_filter_sent_outreach(self, test_db: Session, sample_user: User, sample_opportunity: Opportunity):
        """Test filtering sent vs draft outreach."""
        # Create mix of sent and draft outreach
        for i in range(3):
            outreach = Outreach(
                user_id=sample_user.user_id,
                opportunity_id=sample_opportunity.opportunity_id,
                generated_email=f"Email {i}",
                sent_at=datetime.utcnow() if i % 2 == 0 else None
            )
            test_db.add(outreach)
        test_db.commit()
        
        sent_outreach = test_db.query(Outreach).filter(Outreach.sent_at.isnot(None)).all()
        drafts = test_db.query(Outreach).filter(Outreach.sent_at.is_(None)).all()
        
        assert len(sent_outreach) == 2
        assert len(drafts) == 1

