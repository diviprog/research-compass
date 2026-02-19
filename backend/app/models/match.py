from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Match(Base):
    """Match model for storing semantic matches between users and opportunities."""
    
    __tablename__ = "matches"
    
    # Primary Key
    match_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.opportunity_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Match Details
    match_score = Column(Float, nullable=False, index=True, comment="Semantic similarity score between 0 and 1")
    fit_rationale = Column(Text, nullable=True, comment="AI-generated explanation of why this opportunity matches the user")
    
    # User Interaction
    user_status = Column(String(50), nullable=False, default="pending", index=True, comment="saved, dismissed, contacted, pending")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="matches")
    opportunity = relationship("Opportunity", back_populates="matches")
    
    def __repr__(self):
        return f"<Match(id={self.match_id}, user_id={self.user_id}, opp_id={self.opportunity_id}, score={self.match_score:.3f})>"
    
    def to_dict(self):
        """Serialize model to dictionary for API responses."""
        return {
            "match_id": self.match_id,
            "user_id": self.user_id,
            "opportunity_id": self.opportunity_id,
            "match_score": round(self.match_score, 3),
            "fit_rationale": self.fit_rationale,
            "user_status": self.user_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

