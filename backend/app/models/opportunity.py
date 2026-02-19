from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Opportunity(Base):
    """Opportunity model for storing research opportunities discovered from web scraping."""
    
    __tablename__ = "opportunities"
    
    # Primary Key
    opportunity_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Source Information
    source_url = Column(String(1000), nullable=False, unique=True, index=True, comment="Original URL where opportunity was found")
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="When the opportunity was first scraped")
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="Last time the opportunity was re-scraped/updated")
    
    # Basic Information
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False, comment="Full description of the opportunity")
    lab_name = Column(String(255), nullable=True, index=True)
    pi_name = Column(String(255), nullable=True, index=True, comment="Principal Investigator name")
    institution = Column(String(255), nullable=True, index=True)
    
    # Research Details
    research_topics = Column(JSON, nullable=True, comment="List of research topics/domains")
    methods = Column(JSON, nullable=True, comment="List of methods and techniques")
    datasets = Column(JSON, nullable=True, comment="List of datasets and tools mentioned")
    
    # Application Details
    deadline = Column(DateTime, nullable=True, index=True, comment="Application deadline if specified")
    funding_status = Column(String(100), nullable=True, comment="funded, unfunded, tbd")
    experience_required = Column(String(100), nullable=True, comment="Required experience level")
    contact_email = Column(String(255), nullable=True)
    application_link = Column(String(1000), nullable=True, comment="Link to application form/page")
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether the opportunity is still active")
    
    # Hard Filter Fields (for matching algorithm)
    location_city = Column(String(100), nullable=True, comment="City where position is located")
    location_state = Column(String(2), nullable=True, index=True, comment="State code (e.g., 'CA', 'NY')")
    is_remote = Column(Boolean, default=False, nullable=False, comment="Can be done remotely")
    degree_levels = Column(ARRAY(String), nullable=True, comment="Accepted degree levels: ['undergraduate', 'masters', 'phd']")
    min_hours = Column(Integer, nullable=True, comment="Minimum hours per week expected")
    max_hours = Column(Integer, nullable=True, comment="Maximum hours per week allowed")
    paid_type = Column(String(50), nullable=True, comment="Type of compensation: 'stipend', 'hourly', 'unpaid', 'credit'")
    
    # Relationships
    matches = relationship("Match", back_populates="opportunity", cascade="all, delete-orphan")
    outreach_history = relationship("Outreach", back_populates="opportunity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Opportunity(id={self.opportunity_id}, title='{self.title}', lab='{self.lab_name}')>"
    
    def to_dict(self):
        """Serialize model to dictionary for API responses."""
        return {
            "opportunity_id": self.opportunity_id,
            "source_url": self.source_url,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "title": self.title,
            "description": self.description,
            "lab_name": self.lab_name,
            "pi_name": self.pi_name,
            "institution": self.institution,
            "research_topics": self.research_topics or [],
            "methods": self.methods or [],
            "datasets": self.datasets or [],
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "funding_status": self.funding_status,
            "experience_required": self.experience_required,
            "contact_email": self.contact_email,
            "application_link": self.application_link,
            "is_active": self.is_active,
            "location_city": self.location_city,
            "location_state": self.location_state,
            "is_remote": self.is_remote,
            "degree_levels": self.degree_levels or [],
            "min_hours": self.min_hours,
            "max_hours": self.max_hours,
            "paid_type": self.paid_type,
        }

