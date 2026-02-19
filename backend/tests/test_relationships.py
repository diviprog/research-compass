"""
Tests for model relationships, foreign keys, and cascade operations.
"""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import User, Opportunity, Match, Outreach


class TestUserRelationships:
    """Tests for User model relationships."""
    
    def test_user_has_matches(self, test_db: Session, sample_user: User, sample_opportunity: Opportunity):
        """Test that user has access to their matches."""
        # Create multiple matches for the user
        for i in range(3):
            match = Match(
                user_id=sample_user.user_id,
                opportunity_id=sample_opportunity.opportunity_id,
                match_score=0.8 - (i * 0.1),
                user_status="pending"
            )
            test_db.add(match)
        test_db.commit()
        
        test_db.refresh(sample_user)
        assert len(sample_user.matches) == 3
        assert all(isinstance(m, Match) for m in sample_user.matches)
    
    def test_user_has_outreach_history(self, test_db: Session, sample_user: User, sample_opportunity: Opportunity):
        """Test that user has access to their outreach history."""
        # Create multiple outreach records
        for i in range(2):
            outreach = Outreach(
                user_id=sample_user.user_id,
                opportunity_id=sample_opportunity.opportunity_id,
                generated_email=f"Email {i}"
            )
            test_db.add(outreach)
        test_db.commit()
        
        test_db.refresh(sample_user)
        assert len(sample_user.outreach_history) == 2
        assert all(isinstance(o, Outreach) for o in sample_user.outreach_history)
    
    def test_delete_user_cascades_to_matches(self, test_db: Session, sample_match: Match):
        """Test that deleting a user cascades to delete their matches."""
        user_id = sample_match.user_id
        match_id = sample_match.match_id
        
        # Delete user
        user = test_db.query(User).filter(User.user_id == user_id).first()
        test_db.delete(user)
        test_db.commit()
        
        # Check that match was also deleted
        deleted_match = test_db.query(Match).filter(Match.match_id == match_id).first()
        assert deleted_match is None
    
    def test_delete_user_cascades_to_outreach(self, test_db: Session, sample_outreach: Outreach):
        """Test that deleting a user cascades to delete their outreach."""
        user_id = sample_outreach.user_id
        outreach_id = sample_outreach.outreach_id
        
        # Delete user
        user = test_db.query(User).filter(User.user_id == user_id).first()
        test_db.delete(user)
        test_db.commit()
        
        # Check that outreach was also deleted
        deleted_outreach = test_db.query(Outreach).filter(
            Outreach.outreach_id == outreach_id
        ).first()
        assert deleted_outreach is None


class TestOpportunityRelationships:
    """Tests for Opportunity model relationships."""
    
    def test_opportunity_has_matches(self, test_db: Session, sample_user: User, sample_opportunity: Opportunity):
        """Test that opportunity has access to its matches."""
        # Create multiple matches for the opportunity
        for i in range(3):
            match = Match(
                user_id=sample_user.user_id,
                opportunity_id=sample_opportunity.opportunity_id,
                match_score=0.9 - (i * 0.1),
                user_status="pending"
            )
            test_db.add(match)
        test_db.commit()
        
        test_db.refresh(sample_opportunity)
        assert len(sample_opportunity.matches) == 3
        assert all(isinstance(m, Match) for m in sample_opportunity.matches)
    
    def test_opportunity_has_outreach_history(self, test_db: Session, sample_user: User, sample_opportunity: Opportunity):
        """Test that opportunity has access to its outreach history."""
        # Create multiple outreach records
        for i in range(2):
            outreach = Outreach(
                user_id=sample_user.user_id,
                opportunity_id=sample_opportunity.opportunity_id,
                generated_email=f"Email {i}"
            )
            test_db.add(outreach)
        test_db.commit()
        
        test_db.refresh(sample_opportunity)
        assert len(sample_opportunity.outreach_history) == 2
        assert all(isinstance(o, Outreach) for o in sample_opportunity.outreach_history)
    
    def test_delete_opportunity_cascades_to_matches(self, test_db: Session, sample_match: Match):
        """Test that deleting an opportunity cascades to delete its matches."""
        opportunity_id = sample_match.opportunity_id
        match_id = sample_match.match_id
        
        # Delete opportunity
        opp = test_db.query(Opportunity).filter(
            Opportunity.opportunity_id == opportunity_id
        ).first()
        test_db.delete(opp)
        test_db.commit()
        
        # Check that match was also deleted
        deleted_match = test_db.query(Match).filter(Match.match_id == match_id).first()
        assert deleted_match is None
    
    def test_delete_opportunity_cascades_to_outreach(self, test_db: Session, sample_outreach: Outreach):
        """Test that deleting an opportunity cascades to delete its outreach."""
        opportunity_id = sample_outreach.opportunity_id
        outreach_id = sample_outreach.outreach_id
        
        # Delete opportunity
        opp = test_db.query(Opportunity).filter(
            Opportunity.opportunity_id == opportunity_id
        ).first()
        test_db.delete(opp)
        test_db.commit()
        
        # Check that outreach was also deleted
        deleted_outreach = test_db.query(Outreach).filter(
            Outreach.outreach_id == outreach_id
        ).first()
        assert deleted_outreach is None


class TestMatchRelationships:
    """Tests for Match model relationships."""
    
    def test_match_has_user(self, test_db: Session, sample_match: Match, sample_user: User):
        """Test that match can access its user."""
        test_db.refresh(sample_match)
        assert sample_match.user is not None
        assert sample_match.user.user_id == sample_user.user_id
        assert sample_match.user.email == sample_user.email
    
    def test_match_has_opportunity(self, test_db: Session, sample_match: Match, sample_opportunity: Opportunity):
        """Test that match can access its opportunity."""
        test_db.refresh(sample_match)
        assert sample_match.opportunity is not None
        assert sample_match.opportunity.opportunity_id == sample_opportunity.opportunity_id
        assert sample_match.opportunity.title == sample_opportunity.title
    
    def test_match_requires_valid_user_id(self, test_db: Session, sample_opportunity: Opportunity):
        """Test that match cannot be created with invalid user_id."""
        match = Match(
            user_id=99999,  # Non-existent user
            opportunity_id=sample_opportunity.opportunity_id,
            match_score=0.8,
            user_status="pending"
        )
        test_db.add(match)
        
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    def test_match_requires_valid_opportunity_id(self, test_db: Session, sample_user: User):
        """Test that match cannot be created with invalid opportunity_id."""
        match = Match(
            user_id=sample_user.user_id,
            opportunity_id=99999,  # Non-existent opportunity
            match_score=0.8,
            user_status="pending"
        )
        test_db.add(match)
        
        with pytest.raises(IntegrityError):
            test_db.commit()


class TestOutreachRelationships:
    """Tests for Outreach model relationships."""
    
    def test_outreach_has_user(self, test_db: Session, sample_outreach: Outreach, sample_user: User):
        """Test that outreach can access its user."""
        test_db.refresh(sample_outreach)
        assert sample_outreach.user is not None
        assert sample_outreach.user.user_id == sample_user.user_id
        assert sample_outreach.user.name == sample_user.name
    
    def test_outreach_has_opportunity(self, test_db: Session, sample_outreach: Outreach, sample_opportunity: Opportunity):
        """Test that outreach can access its opportunity."""
        test_db.refresh(sample_outreach)
        assert sample_outreach.opportunity is not None
        assert sample_outreach.opportunity.opportunity_id == sample_opportunity.opportunity_id
        assert sample_outreach.opportunity.lab_name == sample_opportunity.lab_name
    
    def test_outreach_requires_valid_user_id(self, test_db: Session, sample_opportunity: Opportunity):
        """Test that outreach cannot be created with invalid user_id."""
        outreach = Outreach(
            user_id=99999,  # Non-existent user
            opportunity_id=sample_opportunity.opportunity_id,
            generated_email="Test email"
        )
        test_db.add(outreach)
        
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    def test_outreach_requires_valid_opportunity_id(self, test_db: Session, sample_user: User):
        """Test that outreach cannot be created with invalid opportunity_id."""
        outreach = Outreach(
            user_id=sample_user.user_id,
            opportunity_id=99999,  # Non-existent opportunity
            generated_email="Test email"
        )
        test_db.add(outreach)
        
        with pytest.raises(IntegrityError):
            test_db.commit()


class TestComplexQueries:
    """Tests for complex queries across relationships."""
    
    def test_query_matches_with_opportunity_details(self, test_db: Session, sample_match: Match):
        """Test querying matches with joined opportunity data."""
        matches = test_db.query(Match).join(Opportunity).filter(
            Opportunity.institution == "MIT"
        ).all()
        
        assert len(matches) == 1
        assert matches[0].opportunity.institution == "MIT"
    
    def test_query_user_matches_by_score(self, test_db: Session, sample_user: User, sample_opportunity: Opportunity):
        """Test querying a user's high-scoring matches."""
        # Create matches with different scores
        for score in [0.9, 0.7, 0.5]:
            match = Match(
                user_id=sample_user.user_id,
                opportunity_id=sample_opportunity.opportunity_id,
                match_score=score,
                user_status="pending"
            )
            test_db.add(match)
        test_db.commit()
        
        high_matches = test_db.query(Match).filter(
            Match.user_id == sample_user.user_id,
            Match.match_score >= 0.7
        ).all()
        
        assert len(high_matches) == 2
    
    def test_count_user_opportunities(self, test_db: Session, sample_user: User):
        """Test counting opportunities matched to a user."""
        # Create multiple opportunities and matches
        for i in range(5):
            opp = Opportunity(
                source_url=f"https://example.com/opp-{i}",
                title=f"Opportunity {i}",
                description="Test",
                lab_name="Lab",
                pi_name="PI",
                institution="University",
                is_active=True
            )
            test_db.add(opp)
            test_db.flush()
            
            match = Match(
                user_id=sample_user.user_id,
                opportunity_id=opp.opportunity_id,
                match_score=0.8,
                user_status="pending"
            )
            test_db.add(match)
        test_db.commit()
        
        match_count = test_db.query(Match).filter(
            Match.user_id == sample_user.user_id
        ).count()
        
        assert match_count == 5

