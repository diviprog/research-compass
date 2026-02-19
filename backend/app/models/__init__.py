"""
Database models for Research Assistant.

This module exports all SQLAlchemy models for easy import.
"""

from app.models.user import User
from app.models.opportunity import Opportunity
from app.models.match import Match
from app.models.outreach import Outreach
from app.models.refresh_token import RefreshToken
from app.models.user_embedding import UserEmbedding
from app.models.opportunity_embedding import OpportunityEmbedding

__all__ = [
    "User",
    "Opportunity",
    "Match",
    "Outreach",
    "RefreshToken",
    "UserEmbedding",
    "OpportunityEmbedding",
]

