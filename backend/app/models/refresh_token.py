from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.db.base import Base


class RefreshToken(Base):
    """Refresh token model for JWT authentication with token blacklisting support."""
    
    __tablename__ = "refresh_tokens"
    
    # Primary Key
    token_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Token Information
    token = Column(String(500), unique=True, nullable=False, index=True, comment="Refresh token string")
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Token Status
    is_revoked = Column(Boolean, default=False, nullable=False, comment="True if token has been blacklisted")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="Token creation timestamp")
    expires_at = Column(DateTime, nullable=False, comment="Token expiration timestamp")
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    def __repr__(self):
        return f"<RefreshToken(token_id={self.token_id}, user_id={self.user_id}, is_revoked={self.is_revoked})>"
    
    def is_expired(self):
        """Check if the refresh token has expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if the refresh token is valid (not expired and not revoked)."""
        return not self.is_expired() and not self.is_revoked

