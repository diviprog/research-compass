from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Outreach(Base):
    """Outreach model for tracking generated emails and user interactions."""
    
    __tablename__ = "outreach"
    
    # Primary Key
    outreach_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.opportunity_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Email Content
    generated_email = Column(Text, nullable=False, comment="AI-generated outreach email")
    user_edited_email = Column(Text, nullable=True, comment="User's edited version of the email")
    
    # Tracking
    sent_at = Column(DateTime, nullable=True, index=True, comment="When the email was actually sent")
    response_received = Column(Boolean, default=False, nullable=False, comment="Whether a response was received")
    response_text = Column(Text, nullable=True, comment="Text of the response if received")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="outreach_history")
    opportunity = relationship("Opportunity", back_populates="outreach_history")
    
    def __repr__(self):
        status = "sent" if self.sent_at else "draft"
        return f"<Outreach(id={self.outreach_id}, user_id={self.user_id}, opp_id={self.opportunity_id}, status={status})>"
    
    def to_dict(self):
        """Serialize model to dictionary for API responses."""
        return {
            "outreach_id": self.outreach_id,
            "user_id": self.user_id,
            "opportunity_id": self.opportunity_id,
            "generated_email": self.generated_email,
            "user_edited_email": self.user_edited_email,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "response_received": self.response_received,
            "response_text": self.response_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

