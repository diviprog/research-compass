"""
Search service for finding opportunities using semantic search + hard filters.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import os

from app.models.opportunity import Opportunity
from app.models.opportunity_embedding import OpportunityEmbedding
from app.services.embeddings import EmbeddingService
from app.schemas.search import SearchFilters


class SearchService:
    """Service for searching opportunities with semantic similarity."""
    
    def __init__(self):
        """Initialize search service with embedding generator."""
        self.embedding_service = EmbeddingService()
    
    def search_opportunities(
        self,
        query: str,
        filters: Optional[SearchFilters],
        limit: int,
        db: Session
    ) -> List[tuple]:
        """
        Search for opportunities using natural language query.
        
        Process:
        1. Generate embedding from query text (on-the-fly)
        2. Apply hard filters to narrow search space
        3. Use pgvector to find semantically similar opportunities
        4. Return ranked results with similarity scores
        
        Args:
            query: Natural language search query
            filters: Optional filters (location, degree, etc.)
            limit: Max number of results
            db: Database session
            
        Returns:
            List of (Opportunity, similarity_score) tuples, ranked by relevance
        """
        # 1. Generate embedding from query text
        query_embedding = self.embedding_service._generate_embedding(query)
        
        # 2. Build base query with JOIN
        base_query = db.query(
            Opportunity,
            OpportunityEmbedding.embedding.cosine_distance(query_embedding).label('distance')
        ).join(
            OpportunityEmbedding,
            Opportunity.opportunity_id == OpportunityEmbedding.opportunity_id
        )
        
        # 3. Apply hard filters
        filter_conditions = [Opportunity.is_active == True]
        
        if filters:
            # Location filter
            if filters.states:
                location_condition = or_(
                    Opportunity.location_state.in_(filters.states),
                    Opportunity.is_remote == True  # Remote positions match any location
                )
                filter_conditions.append(location_condition)
            
            # Remote-only filter
            if filters.is_remote is not None:
                filter_conditions.append(Opportunity.is_remote == filters.is_remote)
            
            # Degree level filter
            if filters.degree_level:
                filter_conditions.append(
                    Opportunity.degree_levels.contains([filters.degree_level])
                )
            
            # Paid type filter
            if filters.paid_type:
                filter_conditions.append(Opportunity.paid_type == filters.paid_type)
            
            # Hours filter
            if filters.min_hours is not None:
                filter_conditions.append(
                    or_(
                        Opportunity.max_hours == None,
                        Opportunity.max_hours >= filters.min_hours
                    )
                )
            
            if filters.max_hours is not None:
                filter_conditions.append(
                    or_(
                        Opportunity.min_hours == None,
                        Opportunity.min_hours <= filters.max_hours
                    )
                )
        
        # Apply all filters
        query = base_query.filter(and_(*filter_conditions))
        
        # 4. Order by similarity (distance) and limit results
        results = query.order_by('distance').limit(limit).all()
        
        # 5. Convert distance to similarity score (0-1, higher is better)
        # Cosine distance is 0-2, we convert to similarity: 1 - (distance/2)
        results_with_similarity = [
            (opp, 1.0 - (distance / 2.0))
            for opp, distance in results
        ]
        
        return results_with_similarity
    
    def get_total_opportunities_count(self, db: Session) -> int:
        """Get total number of active opportunities in database."""
        return db.query(Opportunity).filter(Opportunity.is_active == True).count()

