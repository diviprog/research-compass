"""
API endpoints for semantic search of research opportunities.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.services.search import SearchService


router = APIRouter(prefix="/opportunities", tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search_opportunities(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for research opportunities using natural language.
    
    **How it works:**
    1. Takes your research interests as natural language text
    2. Converts text to an embedding (vector) using AI
    3. Finds opportunities with similar embeddings (semantic search)
    4. Applies optional filters (location, degree level, etc.)
    5. Returns ranked results based on similarity
    
    **No account required!** Just type what you're interested in.
    
    **Example queries:**
    - "I want to research machine learning for medical imaging"
    - "Interested in climate change and renewable energy"
    - "Computer vision for autonomous vehicles"
    - "Neuroscience and brain-computer interfaces"
    
    **Example request:**
    ```json
    {
      "query": "I want to work on AI for healthcare",
      "filters": {
        "states": ["CA", "NY"],
        "degree_level": "undergraduate",
        "is_remote": false
      },
      "limit": 20
    }
    ```
    
    **Response:**
    - Ranked list of opportunities
    - Similarity scores (0-1, higher = better match)
    - Full opportunity details
    """
    try:
        # Initialize search service
        search_service = SearchService()
        
        # Perform search
        results = search_service.search_opportunities(
            query=request.query,
            filters=request.filters,
            limit=request.limit,
            db=db
        )
        
        # Get total count for context
        total_opps = search_service.get_total_opportunities_count(db)
        
        # Format results
        result_items = []
        for opportunity, similarity_score in results:
            result_items.append(
                SearchResultItem(
                    opportunity_id=opportunity.opportunity_id,
                    title=opportunity.title,
                    description=opportunity.description,
                    lab_name=opportunity.lab_name,
                    pi_name=opportunity.pi_name,
                    institution=opportunity.institution,
                    location_city=opportunity.location_city,
                    location_state=opportunity.location_state,
                    is_remote=opportunity.is_remote or False,
                    degree_levels=opportunity.degree_levels or [],
                    paid_type=opportunity.paid_type,
                    min_hours=opportunity.min_hours,
                    max_hours=opportunity.max_hours,
                    research_topics=opportunity.research_topics or [],
                    deadline=opportunity.deadline.isoformat() if opportunity.deadline else None,
                    application_link=opportunity.application_link,
                    contact_email=opportunity.contact_email,
                    similarity_score=similarity_score
                )
            )
        
        return SearchResponse(
            query=request.query,
            results=result_items,
            count=len(result_items),
            total_opportunities=total_opps,
            filters_applied=request.filters
        )
        
    except ValueError as e:
        # OpenAI API key not set or other config issue
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Search service unavailable: {str(e)}"
        )
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/search/test")
def test_search_setup(db: Session = Depends(get_db)):
    """
    Test endpoint to verify search is properly configured.
    
    Returns:
    - Number of opportunities with embeddings
    - Number of opportunities without embeddings
    - Search readiness status
    """
    from app.models.opportunity_embedding import OpportunityEmbedding
    from app.models.opportunity import Opportunity
    import os
    
    total_opps = db.query(Opportunity).filter(Opportunity.is_active == True).count()
    opps_with_embeddings = db.query(OpportunityEmbedding).count()
    
    has_api_key = bool(os.getenv("OPENAI_API_KEY"))
    
    is_ready = has_api_key and opps_with_embeddings > 0
    
    return {
        "ready": is_ready,
        "has_openai_key": has_api_key,
        "total_opportunities": total_opps,
        "opportunities_with_embeddings": opps_with_embeddings,
        "opportunities_without_embeddings": total_opps - opps_with_embeddings,
        "message": "Search is ready!" if is_ready else "Setup needed: generate opportunity embeddings first"
    }

