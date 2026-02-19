"""
API endpoints for generating and managing embeddings.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from app.db.database import get_db
from app.services.embeddings import EmbeddingService
from app.models.user import User


router = APIRouter(prefix="/embeddings", tags=["embeddings"])


@router.post("/users/{user_id}")
def generate_user_embedding(
    user_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Generate embedding for a specific user's research interests.
    
    This endpoint:
    1. Extracts the user's research_interests text
    2. Sends it to OpenAI API
    3. Stores the resulting 1536-dim vector in user_embeddings table
    
    **Use case:** Call this after a user updates their profile
    """
    try:
        service = EmbeddingService()
        embedding = service.generate_user_embedding(user_id, db)
        
        return {
            "success": True,
            "message": f"Embedding generated for user {user_id}",
            "user_id": embedding.user_id,
            "model": embedding.model_name,
            "embedded_at": embedding.embedded_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding: {str(e)}"
        )


@router.post("/opportunities/{opportunity_id}")
def generate_opportunity_embedding(
    opportunity_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Generate embedding for a specific opportunity.
    
    This endpoint:
    1. Combines title + description + research_topics
    2. Sends combined text to OpenAI API
    3. Stores the resulting 1536-dim vector in opportunity_embeddings table
    
    **Use case:** Call this after scraping/creating a new opportunity
    """
    try:
        service = EmbeddingService()
        embedding = service.generate_opportunity_embedding(opportunity_id, db)
        
        return {
            "success": True,
            "message": f"Embedding generated for opportunity {opportunity_id}",
            "opportunity_id": embedding.opportunity_id,
            "model": embedding.model_name,
            "embedded_at": embedding.embedded_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding: {str(e)}"
        )


@router.post("/users/generate-all")
def generate_all_user_embeddings(
    db: Session = Depends(get_db)
) -> Dict:
    """
    Generate embeddings for all users that don't have them yet.
    
    **Use case:** 
    - Initial setup: Generate embeddings for existing users
    - Batch processing: Catch up on any missed users
    
    **Returns:** Count of success/failed/skipped users
    """
    try:
        service = EmbeddingService()
        results = service.generate_all_user_embeddings(db)
        
        return {
            "success": True,
            "message": "Batch user embedding generation completed",
            **results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embeddings: {str(e)}"
        )


@router.post("/opportunities/generate-all")
def generate_all_opportunity_embeddings(
    db: Session = Depends(get_db)
) -> Dict:
    """
    Generate embeddings for all opportunities that don't have them yet.
    
    **Use case:**
    - Initial setup: Generate embeddings for scraped opportunities
    - After scraping: Batch process new opportunities
    
    **Returns:** Count of success/failed/skipped opportunities
    """
    try:
        service = EmbeddingService()
        results = service.generate_all_opportunity_embeddings(db)
        
        return {
            "success": True,
            "message": "Batch opportunity embedding generation completed",
            **results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embeddings: {str(e)}"
        )


@router.get("/stats")
def get_embedding_stats(db: Session = Depends(get_db)) -> Dict:
    """
    Get statistics about embeddings in the database.
    
    Shows:
    - Total users with embeddings
    - Total opportunities with embeddings
    - Users without embeddings
    - Opportunities without embeddings
    """
    from app.models.user_embedding import UserEmbedding
    from app.models.opportunity_embedding import OpportunityEmbedding
    from app.models.opportunity import Opportunity
    
    total_users = db.query(User).count()
    users_with_embeddings = db.query(UserEmbedding).count()
    
    total_opps = db.query(Opportunity).count()
    opps_with_embeddings = db.query(OpportunityEmbedding).count()
    
    return {
        "users": {
            "total": total_users,
            "with_embeddings": users_with_embeddings,
            "without_embeddings": total_users - users_with_embeddings
        },
        "opportunities": {
            "total": total_opps,
            "with_embeddings": opps_with_embeddings,
            "without_embeddings": total_opps - opps_with_embeddings
        }
    }

