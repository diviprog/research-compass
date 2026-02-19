"""
Pydantic schemas for student profile management.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class Experience(BaseModel):
    """Schema for a single experience entry."""
    title: str = Field(..., description="Position title or role")
    organization: str = Field(..., description="Organization name")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM or text)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM or text, 'Present' if ongoing)")
    description: Optional[str] = Field(None, description="Description of responsibilities and achievements")
    location: Optional[str] = Field(None, description="Location of the position")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "title": "Research Assistant",
                "organization": "MIT Computer Science Lab",
                "start_date": "2024-01",
                "end_date": "Present",
                "description": "Conducted research on machine learning algorithms for natural language processing",
                "location": "Cambridge, MA"
            }]
        }
    }


class Publication(BaseModel):
    """Schema for a publication entry."""
    title: str = Field(..., description="Publication title")
    authors: List[str] = Field(..., description="List of authors")
    venue: Optional[str] = Field(None, description="Conference or journal name")
    year: Optional[int] = Field(None, description="Publication year")
    url: Optional[str] = Field(None, description="Link to publication")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "title": "Deep Learning for Text Classification",
                "authors": ["John Doe", "Jane Smith"],
                "venue": "NeurIPS 2024",
                "year": 2024,
                "url": "https://arxiv.org/abs/..."
            }]
        }
    }


class ProfileCreate(BaseModel):
    """Schema for creating a student profile."""
    # University Information
    university: str = Field(..., min_length=1, max_length=255, description="Current university")
    major: str = Field(..., min_length=1, max_length=255, description="Major or field of study")
    graduation_year: int = Field(..., ge=2000, le=2050, description="Expected or actual graduation year")
    gpa: Optional[str] = Field(None, max_length=10, description="GPA (e.g., '3.8/4.0')")

    # Resume and Experience
    resume_text: Optional[str] = Field(None, description="Resume summary or parsed text")
    past_experiences: List[Experience] = Field(default_factory=list, description="List of past experiences")
    skills: List[str] = Field(default_factory=list, description="List of technical skills")
    publications: List[Publication] = Field(default_factory=list, description="List of publications")

    # Research Profile
    research_interests: str = Field(..., min_length=10, description="Research interests and goals")
    preferred_methods: List[str] = Field(default_factory=list, description="Preferred research methods")
    preferred_datasets: List[str] = Field(default_factory=list, description="Preferred datasets or tools")

    # User Attributes
    experience_level: Optional[str] = Field(
        default="undergraduate",
        description="Experience level: undergraduate, graduate, postdoc, independent"
    )
    location_preferences: List[str] = Field(default_factory=list, description="Preferred work locations")
    availability: Optional[str] = Field(None, max_length=100, description="Availability: full-time, part-time, remote")

    @field_validator('experience_level')
    @classmethod
    def validate_experience_level(cls, v: str) -> str:
        """Validate experience level is one of allowed values."""
        allowed = ["undergraduate", "graduate", "postdoc", "independent"]
        if v not in allowed:
            raise ValueError(f'Experience level must be one of: {", ".join(allowed)}')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "university": "Massachusetts Institute of Technology",
                "major": "Computer Science",
                "graduation_year": 2026,
                "gpa": "3.9/4.0",
                "resume_text": "Computer Science student with strong background in machine learning...",
                "past_experiences": [
                    {
                        "title": "Research Assistant",
                        "organization": "MIT CSAIL",
                        "start_date": "2024-01",
                        "end_date": "Present",
                        "description": "Working on NLP research",
                        "location": "Cambridge, MA"
                    }
                ],
                "skills": ["Python", "TensorFlow", "PyTorch", "Natural Language Processing"],
                "publications": [],
                "research_interests": "I am interested in applying machine learning to natural language understanding, specifically in developing more interpretable and efficient models for text analysis.",
                "preferred_methods": ["Deep Learning", "Statistical Analysis"],
                "preferred_datasets": ["ImageNet", "GLUE"],
                "experience_level": "undergraduate",
                "location_preferences": ["Boston, MA", "Remote"],
                "availability": "part-time"
            }]
        }
    }


class ProfileUpdate(BaseModel):
    """Schema for updating a student profile (all fields optional)."""
    # University Information
    university: Optional[str] = Field(None, min_length=1, max_length=255)
    major: Optional[str] = Field(None, min_length=1, max_length=255)
    graduation_year: Optional[int] = Field(None, ge=2000, le=2050)
    gpa: Optional[str] = Field(None, max_length=10)

    # Resume and Experience
    resume_text: Optional[str] = None
    past_experiences: Optional[List[Experience]] = None
    skills: Optional[List[str]] = None
    publications: Optional[List[Publication]] = None

    # Research Profile
    research_interests: Optional[str] = Field(None, min_length=10)
    preferred_methods: Optional[List[str]] = None
    preferred_datasets: Optional[List[str]] = None

    # User Attributes
    experience_level: Optional[str] = None
    location_preferences: Optional[List[str]] = None
    availability: Optional[str] = Field(None, max_length=100)

    @field_validator('experience_level')
    @classmethod
    def validate_experience_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate experience level is one of allowed values."""
        if v is None:
            return v
        allowed = ["undergraduate", "graduate", "postdoc", "independent"]
        if v not in allowed:
            raise ValueError(f'Experience level must be one of: {", ".join(allowed)}')
        return v


class ProfileResponse(BaseModel):
    """Schema for profile data in API responses."""
    user_id: int
    email: str
    name: str

    # University Information
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[str] = None

    # Resume and Experience
    resume_file_path: Optional[str] = None
    resume_text: Optional[str] = None
    past_experiences: List[dict] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    publications: List[dict] = Field(default_factory=list)

    # Research Profile
    research_interests: str
    preferred_methods: List[str] = Field(default_factory=list)
    preferred_datasets: List[str] = Field(default_factory=list)

    # User Attributes
    experience_level: str
    location_preferences: List[str] = Field(default_factory=list)
    availability: Optional[str] = None

    # Timestamps
    created_at: str
    updated_at: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [{
                "user_id": 1,
                "email": "student@mit.edu",
                "name": "Jane Doe",
                "university": "MIT",
                "major": "Computer Science",
                "graduation_year": 2026,
                "gpa": "3.9/4.0",
                "resume_text": "Computer Science student...",
                "past_experiences": [],
                "skills": ["Python", "Machine Learning"],
                "publications": [],
                "research_interests": "Machine learning and NLP",
                "preferred_methods": ["Deep Learning"],
                "preferred_datasets": ["ImageNet"],
                "experience_level": "undergraduate",
                "location_preferences": ["Boston, MA"],
                "availability": "part-time",
                "created_at": "2025-10-25T12:00:00",
                "updated_at": "2025-10-25T12:00:00"
            }]
        }
    }
