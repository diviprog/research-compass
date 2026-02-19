"""
Pydantic schemas for opportunity search.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class SearchFilters(BaseModel):
    """Optional filters for narrowing search results."""
    
    states: Optional[List[str]] = Field(
        None,
        description="List of state codes to filter by (e.g., ['CA', 'NY'])"
    )
    degree_level: Optional[str] = Field(
        None,
        description="Degree level: 'undergraduate', 'masters', or 'phd'"
    )
    is_remote: Optional[bool] = Field(
        None,
        description="Filter for remote opportunities only"
    )
    paid_type: Optional[str] = Field(
        None,
        description="Compensation type: 'stipend', 'hourly', 'unpaid', 'credit'"
    )
    min_hours: Optional[int] = Field(
        None,
        description="Minimum hours per week available"
    )
    max_hours: Optional[int] = Field(
        None,
        description="Maximum hours per week available"
    )


class SearchRequest(BaseModel):
    """Request body for opportunity search."""
    
    query: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Natural language description of research interests",
        examples=["I want to research machine learning for medical imaging"]
    )
    filters: Optional[SearchFilters] = Field(
        None,
        description="Optional filters to narrow results"
    )
    limit: int = Field(
        20,
        ge=1,
        le=100,
        description="Maximum number of results to return"
    )


class SearchResultItem(BaseModel):
    """Single search result with opportunity details."""
    
    # Basic info
    opportunity_id: int
    title: str
    description: str
    lab_name: Optional[str]
    pi_name: Optional[str]
    institution: Optional[str]
    
    # Location
    location_city: Optional[str]
    location_state: Optional[str]
    is_remote: bool
    
    # Eligibility
    degree_levels: List[str]
    paid_type: Optional[str]
    min_hours: Optional[int]
    max_hours: Optional[int]
    
    # Research details
    research_topics: List[str]
    
    # Application
    deadline: Optional[str]
    application_link: Optional[str]
    contact_email: Optional[str]
    
    # Match quality
    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Semantic similarity score (0-1, higher is better)"
    )
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Response containing search results."""
    
    query: str = Field(..., description="Original search query")
    results: List[SearchResultItem]
    count: int = Field(..., description="Number of results returned")
    total_opportunities: int = Field(..., description="Total opportunities in database")
    filters_applied: Optional[SearchFilters] = None

