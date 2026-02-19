from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class User(Base):
    """User model for storing researcher profiles and preferences."""
    
    __tablename__ = "users"
    
    # Primary Key
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False, comment="Bcrypt hashed password")
    
    # Basic Information
    name = Column(String(255), nullable=False)
    
    # Student Profile Information
    university = Column(String(255), nullable=True, comment="Student's current university")
    major = Column(String(255), nullable=True, comment="Student's major/field of study")
    graduation_year = Column(Integer, nullable=True, comment="Expected or actual graduation year")
    gpa = Column(String(10), nullable=True, comment="GPA (optional)")

    # Resume and Experience
    resume_file_path = Column(String(500), nullable=True, comment="Path to uploaded resume PDF file")
    resume_text = Column(Text, nullable=True, comment="Parsed resume text or summary")
    past_experiences = Column(JSON, nullable=True, comment="List of past research/work experiences")
    skills = Column(JSON, nullable=True, comment="List of technical skills")
    publications = Column(JSON, nullable=True, comment="List of publications/papers")

    # Research Profile
    research_interests = Column(Text, nullable=False, default="", comment="Free-text description of research interests")
    preferred_methods = Column(JSON, nullable=True, comment="List of preferred research methods")
    preferred_datasets = Column(JSON, nullable=True, comment="List of preferred datasets/tools")

    # User Attributes
    degree_level = Column(String(50), nullable=False, default="undergraduate", comment="undergraduate, masters, phd")
    location_preferences = Column(JSON, nullable=True, comment="Array of preferred state codes: ['CA', 'NY', 'MA']")
    availability = Column(String(100), nullable=True, comment="Commitment level: full-time, part-time, remote")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    matches = relationship("Match", back_populates="user", cascade="all, delete-orphan")
    outreach_history = relationship("Outreach", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.user_id}, email='{self.email}', name='{self.name}')>"
    
    def to_dict(self):
        """Serialize model to dictionary for API responses."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "university": self.university,
            "major": self.major,
            "graduation_year": self.graduation_year,
            "gpa": self.gpa,
            "resume_file_path": self.resume_file_path,
            "resume_text": self.resume_text,
            "past_experiences": self.past_experiences or [],
            "skills": self.skills or [],
            "publications": self.publications or [],
            "research_interests": self.research_interests,
            "preferred_methods": self.preferred_methods or [],
            "preferred_datasets": self.preferred_datasets or [],
            "degree_level": self.degree_level,
            "location_preferences": self.location_preferences or [],
            "availability": self.availability,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

