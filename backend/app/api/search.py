"""
API endpoints for semantic search of research opportunities.
"""

from typing import Optional

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.db.database import get_db
from app.models.opportunity import Opportunity
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem, SearchFilters
from app.services.search import SearchService
from app.services.embeddings import EmbeddingService


router = APIRouter(prefix="/opportunities", tags=["search"])


def _opportunity_to_search_text(opp: Opportunity) -> str:
    """Build text for embedding: title + description + research topics (match EmbeddingService)."""
    parts = []
    if opp.title:
        parts.append(opp.title)
    if opp.description:
        parts.append(opp.description)
    if opp.research_topics:
        parts.append("Research topics: " + ", ".join(opp.research_topics))
    return ". ".join(parts) if parts else ""


def _apply_filters_python(opportunities: list, filters: Optional[SearchFilters]) -> list:
    """Apply search filters in Python (for SQLite fallback)."""
    if not filters:
        return opportunities
    out = []
    for opp in opportunities:
        if filters.states is not None:
            in_state = opp.location_state and opp.location_state in filters.states
            if not in_state and not (opp.is_remote or False):
                continue
        if filters.is_remote is not None and (opp.is_remote or False) != filters.is_remote:
            continue
        if filters.degree_level is not None:
            levels = opp.degree_levels or []
            if filters.degree_level not in levels:
                continue
        if filters.paid_type is not None and opp.paid_type != filters.paid_type:
            continue
        if filters.min_hours is not None:
            if opp.max_hours is not None and opp.max_hours < filters.min_hours:
                continue
        if filters.max_hours is not None:
            if opp.min_hours is not None and opp.min_hours > filters.max_hours:
                continue
        out.append(opp)
    return out


def _cosine_similarity_01(a: list[float], b: list[float]) -> float:
    """Cosine similarity in [0, 1]. Uses (cos + 1) / 2 so score is 0-1."""
    va, vb = np.array(a, dtype=float), np.array(b, dtype=float)
    dot = np.dot(va, vb)
    na, nb = np.linalg.norm(va), np.linalg.norm(vb)
    if na == 0 or nb == 0:
        return 0.0
    cos = dot / (na * nb)
    return float((cos + 1.0) / 2.0)


def _search_fallback_sqlite(
    query: str,
    filters: Optional[SearchFilters],
    limit: int,
    db: Session,
) -> tuple:
    """
    SQLite fallback: embed query, fetch opportunities, embed each (cached), rank by numpy cosine similarity.
    Returns (list of (Opportunity, similarity_score), total_opportunities_count).
    """
    embedding_service = EmbeddingService()
    query_embedding = embedding_service._generate_embedding(query)

    # Fetch all active opportunities and apply filters in Python
    opportunities = db.query(Opportunity).filter(Opportunity.is_active == True).all()
    total_opps = len(opportunities)
    opportunities = _apply_filters_python(opportunities, filters)

    # Per-request cache: opportunity_id -> embedding
    embedding_cache: dict[int, list[float]] = {}
    scored: list[tuple[Opportunity, float]] = []

    for opp in opportunities:
        oid = opp.opportunity_id
        if oid not in embedding_cache:
            text = _opportunity_to_search_text(opp)
            if not text:
                continue
            embedding_cache[oid] = embedding_service._generate_embedding(text)
        opp_emb = embedding_cache[oid]
        score = _cosine_similarity_01(query_embedding, opp_emb)
        scored.append((opp, score))

    # Sort by score descending, take top limit
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit], total_opps


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
    def build_response(results: list, total_opps: int) -> SearchResponse:
        result_items = [
            SearchResultItem(
                opportunity_id=opp.opportunity_id,
                title=opp.title,
                description=opp.description,
                lab_name=opp.lab_name,
                pi_name=opp.pi_name,
                institution=opp.institution,
                location_city=opp.location_city,
                location_state=opp.location_state,
                is_remote=opp.is_remote or False,
                degree_levels=opp.degree_levels or [],
                paid_type=opp.paid_type,
                min_hours=opp.min_hours,
                max_hours=opp.max_hours,
                research_topics=opp.research_topics or [],
                deadline=opp.deadline.isoformat() if opp.deadline else None,
                application_link=opp.application_link,
                contact_email=opp.contact_email,
                similarity_score=score,
            )
            for opp, score in results
        ]
        return SearchResponse(
            query=request.query,
            results=result_items,
            count=len(result_items),
            total_opportunities=total_opps,
            filters_applied=request.filters
        )

    try:
        search_service = SearchService()
        results = search_service.search_opportunities(
            query=request.query,
            filters=request.filters,
            limit=request.limit,
            db=db
        )
        total_opps = search_service.get_total_opportunities_count(db)
        return build_response(results, total_opps)
    except (ImportError, OperationalError, ProgrammingError):
        # pgvector / Postgres unavailable (e.g. SQLite) — use numpy cosine fallback
        try:
            results, total_opps = _search_fallback_sqlite(
                query=request.query,
                filters=request.filters,
                limit=request.limit,
                db=db,
            )
            return build_response(results, total_opps)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Search service unavailable: {str(e)}"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Search service unavailable: {str(e)}"
        )
    except Exception as e:
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

