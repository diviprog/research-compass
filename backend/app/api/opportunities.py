"""
API endpoints for research opportunities.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime

from app.db.database import get_db
from app.models.user import User
from app.models.opportunity import Opportunity
from app.core.auth import get_current_user, get_optional_user
from pydantic import BaseModel, Field


router = APIRouter(prefix="/opportunities", tags=["opportunities"])


# Pydantic schemas for request/response
class OpportunityResponse(BaseModel):
    """Response schema for opportunity data."""
    opportunity_id: int
    source_url: str
    scraped_at: str
    last_updated: str
    title: str
    description: str
    lab_name: Optional[str] = None
    pi_name: Optional[str] = None
    institution: Optional[str] = None
    research_topics: List[str] = []
    methods: List[str] = []
    datasets: List[str] = []
    deadline: Optional[str] = None
    funding_status: Optional[str] = None
    experience_required: Optional[str] = None
    contact_email: Optional[str] = None
    application_link: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class OpportunityCreate(BaseModel):
    """Schema for creating a new opportunity."""
    source_url: str = Field(..., max_length=1000)
    title: str = Field(..., max_length=500)
    description: str
    lab_name: Optional[str] = Field(None, max_length=255)
    pi_name: Optional[str] = Field(None, max_length=255)
    institution: Optional[str] = Field(None, max_length=255)
    research_topics: Optional[List[str]] = None
    methods: Optional[List[str]] = None
    datasets: Optional[List[str]] = None
    deadline: Optional[datetime] = None
    funding_status: Optional[str] = Field(None, max_length=100)
    experience_required: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[str] = Field(None, max_length=255)
    application_link: Optional[str] = Field(None, max_length=1000)
    is_active: bool = True


class OpportunityUpdate(BaseModel):
    """Schema for updating an opportunity."""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    lab_name: Optional[str] = Field(None, max_length=255)
    pi_name: Optional[str] = Field(None, max_length=255)
    institution: Optional[str] = Field(None, max_length=255)
    research_topics: Optional[List[str]] = None
    methods: Optional[List[str]] = None
    datasets: Optional[List[str]] = None
    deadline: Optional[datetime] = None
    funding_status: Optional[str] = Field(None, max_length=100)
    experience_required: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[str] = Field(None, max_length=255)
    application_link: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None


@router.get("/", response_model=List[OpportunityResponse])
async def list_opportunities(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in title, description, lab name"),
    institution: Optional[str] = Query(None, description="Filter by institution"),
    funding_status: Optional[str] = Query(None, description="Filter by funding status"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Get a list of research opportunities with optional filtering.
    Authentication is optional.
    """
    query = db.query(Opportunity)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Opportunity.is_active == is_active)
    
    if institution:
        query = query.filter(Opportunity.institution.ilike(f"%{institution}%"))
    
    if funding_status:
        query = query.filter(Opportunity.funding_status == funding_status)
    
    if search:
        search_filter = or_(
            Opportunity.title.ilike(f"%{search}%"),
            Opportunity.description.ilike(f"%{search}%"),
            Opportunity.lab_name.ilike(f"%{search}%"),
            Opportunity.pi_name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Order by most recently updated first
    query = query.order_by(Opportunity.last_updated.desc())
    
    # Apply pagination
    opportunities = query.offset(skip).limit(limit).all()
    
    # Convert to response format
    return [OpportunityResponse(
        opportunity_id=opp.opportunity_id,
        source_url=opp.source_url,
        scraped_at=opp.scraped_at.isoformat() if opp.scraped_at else "",
        last_updated=opp.last_updated.isoformat() if opp.last_updated else "",
        title=opp.title,
        description=opp.description,
        lab_name=opp.lab_name,
        pi_name=opp.pi_name,
        institution=opp.institution,
        research_topics=opp.research_topics or [],
        methods=opp.methods or [],
        datasets=opp.datasets or [],
        deadline=opp.deadline.isoformat() if opp.deadline else None,
        funding_status=opp.funding_status,
        experience_required=opp.experience_required,
        contact_email=opp.contact_email,
        application_link=opp.application_link,
        is_active=opp.is_active
    ) for opp in opportunities]


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific opportunity by ID.
    Requires authentication.
    """
    opportunity = db.query(Opportunity).filter(
        Opportunity.opportunity_id == opportunity_id
    ).first()
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return OpportunityResponse(
        opportunity_id=opportunity.opportunity_id,
        source_url=opportunity.source_url,
        scraped_at=opportunity.scraped_at.isoformat() if opportunity.scraped_at else "",
        last_updated=opportunity.last_updated.isoformat() if opportunity.last_updated else "",
        title=opportunity.title,
        description=opportunity.description,
        lab_name=opportunity.lab_name,
        pi_name=opportunity.pi_name,
        institution=opportunity.institution,
        research_topics=opportunity.research_topics or [],
        methods=opportunity.methods or [],
        datasets=opportunity.datasets or [],
        deadline=opportunity.deadline.isoformat() if opportunity.deadline else None,
        funding_status=opportunity.funding_status,
        experience_required=opportunity.experience_required,
        contact_email=opportunity.contact_email,
        application_link=opportunity.application_link,
        is_active=opportunity.is_active
    )


@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new research opportunity.
    Requires authentication.
    """
    # Check if URL already exists
    existing = db.query(Opportunity).filter(
        Opportunity.source_url == opportunity_data.source_url
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An opportunity with this URL already exists"
        )
    
    # Create new opportunity
    new_opportunity = Opportunity(
        source_url=opportunity_data.source_url,
        title=opportunity_data.title,
        description=opportunity_data.description,
        lab_name=opportunity_data.lab_name,
        pi_name=opportunity_data.pi_name,
        institution=opportunity_data.institution,
        research_topics=opportunity_data.research_topics,
        methods=opportunity_data.methods,
        datasets=opportunity_data.datasets,
        deadline=opportunity_data.deadline,
        funding_status=opportunity_data.funding_status,
        experience_required=opportunity_data.experience_required,
        contact_email=opportunity_data.contact_email,
        application_link=opportunity_data.application_link,
        is_active=opportunity_data.is_active
    )
    
    db.add(new_opportunity)
    db.commit()
    db.refresh(new_opportunity)
    
    return OpportunityResponse(
        opportunity_id=new_opportunity.opportunity_id,
        source_url=new_opportunity.source_url,
        scraped_at=new_opportunity.scraped_at.isoformat() if new_opportunity.scraped_at else "",
        last_updated=new_opportunity.last_updated.isoformat() if new_opportunity.last_updated else "",
        title=new_opportunity.title,
        description=new_opportunity.description,
        lab_name=new_opportunity.lab_name,
        pi_name=new_opportunity.pi_name,
        institution=new_opportunity.institution,
        research_topics=new_opportunity.research_topics or [],
        methods=new_opportunity.methods or [],
        datasets=new_opportunity.datasets or [],
        deadline=new_opportunity.deadline.isoformat() if new_opportunity.deadline else None,
        funding_status=new_opportunity.funding_status,
        experience_required=new_opportunity.experience_required,
        contact_email=new_opportunity.contact_email,
        application_link=new_opportunity.application_link,
        is_active=new_opportunity.is_active
    )


@router.put("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    opportunity_data: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing opportunity.
    Requires authentication.
    """
    opportunity = db.query(Opportunity).filter(
        Opportunity.opportunity_id == opportunity_id
    ).first()
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Update fields if provided
    update_data = opportunity_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opportunity, field, value)
    
    db.commit()
    db.refresh(opportunity)
    
    return OpportunityResponse(
        opportunity_id=opportunity.opportunity_id,
        source_url=opportunity.source_url,
        scraped_at=opportunity.scraped_at.isoformat() if opportunity.scraped_at else "",
        last_updated=opportunity.last_updated.isoformat() if opportunity.last_updated else "",
        title=opportunity.title,
        description=opportunity.description,
        lab_name=opportunity.lab_name,
        pi_name=opportunity.pi_name,
        institution=opportunity.institution,
        research_topics=opportunity.research_topics or [],
        methods=opportunity.methods or [],
        datasets=opportunity.datasets or [],
        deadline=opportunity.deadline.isoformat() if opportunity.deadline else None,
        funding_status=opportunity.funding_status,
        experience_required=opportunity.experience_required,
        contact_email=opportunity.contact_email,
        application_link=opportunity.application_link,
        is_active=opportunity.is_active
    )


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an opportunity (soft delete by setting is_active to False).
    Requires authentication.
    """
    opportunity = db.query(Opportunity).filter(
        Opportunity.opportunity_id == opportunity_id
    ).first()
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Soft delete
    opportunity.is_active = False
    db.commit()
    
    return None

