from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from pgvector.sqlalchemy import Vector
from app.db.base import Base


class UserEmbedding(Base):
    """Stores vector embeddings for user research interests for semantic matching."""
    
    __tablename__ = "user_embeddings"
    
    # Primary Key (also Foreign Key)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    
    # Embedding Details
    model_name = Column(String(100), nullable=False, comment="OpenAI model used (e.g., text-embedding-3-large)")
    text_for_embedding = Column(Text, nullable=False, comment="Copy of research_interests text used for embedding")
    embedding = Column(Vector(3072), nullable=False, comment="3072-dimensional embedding vector")
    
    # Metadata
    embedded_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="When embedding was generated")
    
    # Relationship
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<UserEmbedding(user_id={self.user_id}, model='{self.model_name}')>"
    
    def to_dict(self):
        """Serialize model to dictionary for API responses."""
        return {
            "user_id": self.user_id,
            "model_name": self.model_name,
            "embedded_at": self.embedded_at.isoformat() if self.embedded_at else None,
        }

