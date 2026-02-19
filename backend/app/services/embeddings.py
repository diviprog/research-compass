"""
Embedding generation service using OpenAI API.

This service handles:
- Generating embeddings from text using OpenAI's text-embedding-3-large model
- Storing embeddings in the database
- Updating embeddings when source text changes
"""

from openai import OpenAI
from sqlalchemy.orm import Session
from typing import Optional, List
import os
from datetime import datetime

from app.models.user import User
from app.models.opportunity import Opportunity
from app.models.user_embedding import UserEmbedding
from app.models.opportunity_embedding import OpportunityEmbedding


class EmbeddingService:
    """Service for generating and managing embeddings."""
    
    MODEL_NAME = "text-embedding-3-large"  # 3072 dimensions (default)
    EMBEDDING_DIMENSION = 3072
    
    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector from text using OpenAI API.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of 1536 floats representing the embedding
            
        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            response = self.client.embeddings.create(
                model=self.MODEL_NAME,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    def generate_user_embedding(self, user_id: int, db: Session) -> UserEmbedding:
        """
        Generate and store embedding for a user's research interests.
        
        Args:
            user_id: ID of the user
            db: Database session
            
        Returns:
            UserEmbedding object
            
        Raises:
            ValueError: If user not found or has no research interests
            Exception: If embedding generation fails
        """
        # Get user
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        if not user.research_interests or user.research_interests.strip() == "":
            raise ValueError(f"User {user_id} has no research interests")
        
        # Generate embedding from research interests
        text = user.research_interests.strip()
        embedding_vector = self._generate_embedding(text)
        
        # Check if embedding already exists
        existing = db.query(UserEmbedding).filter(
            UserEmbedding.user_id == user_id
        ).first()
        
        if existing:
            # Update existing embedding
            existing.model_name = self.MODEL_NAME
            existing.text_for_embedding = text
            existing.embedding = embedding_vector
            existing.embedded_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new embedding
            user_embedding = UserEmbedding(
                user_id=user_id,
                model_name=self.MODEL_NAME,
                text_for_embedding=text,
                embedding=embedding_vector,
                embedded_at=datetime.utcnow()
            )
            db.add(user_embedding)
            db.commit()
            db.refresh(user_embedding)
            return user_embedding
    
    def generate_opportunity_embedding(
        self, 
        opportunity_id: int, 
        db: Session
    ) -> OpportunityEmbedding:
        """
        Generate and store embedding for an opportunity.
        
        Combines title, description, and research topics into embedding text.
        
        Args:
            opportunity_id: ID of the opportunity
            db: Database session
            
        Returns:
            OpportunityEmbedding object
            
        Raises:
            ValueError: If opportunity not found
            Exception: If embedding generation fails
        """
        # Get opportunity
        opp = db.query(Opportunity).filter(
            Opportunity.opportunity_id == opportunity_id
        ).first()
        
        if not opp:
            raise ValueError(f"Opportunity {opportunity_id} not found")
        
        # Build text for embedding: title + description + research topics
        parts = []
        
        if opp.title:
            parts.append(opp.title)
        
        if opp.description:
            parts.append(opp.description)
        
        if opp.research_topics:
            topics_str = ", ".join(opp.research_topics)
            parts.append(f"Research topics: {topics_str}")
        
        if not parts:
            raise ValueError(f"Opportunity {opportunity_id} has no content for embedding")
        
        text = ". ".join(parts)
        
        # Generate embedding
        embedding_vector = self._generate_embedding(text)
        
        # Check if embedding already exists
        existing = db.query(OpportunityEmbedding).filter(
            OpportunityEmbedding.opportunity_id == opportunity_id
        ).first()
        
        if existing:
            # Update existing embedding
            existing.model_name = self.MODEL_NAME
            existing.text_for_embedding = text
            existing.embedding = embedding_vector
            existing.embedded_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new embedding
            opp_embedding = OpportunityEmbedding(
                opportunity_id=opportunity_id,
                model_name=self.MODEL_NAME,
                text_for_embedding=text,
                embedding=embedding_vector,
                embedded_at=datetime.utcnow()
            )
            db.add(opp_embedding)
            db.commit()
            db.refresh(opp_embedding)
            return opp_embedding
    
    def generate_all_user_embeddings(self, db: Session) -> dict:
        """
        Generate embeddings for all users that don't have them.
        
        Args:
            db: Database session
            
        Returns:
            Dict with success/failure counts
        """
        users = db.query(User).filter(
            User.research_interests != None,
            User.research_interests != ""
        ).all()
        
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        for user in users:
            # Check if already has embedding
            existing = db.query(UserEmbedding).filter(
                UserEmbedding.user_id == user.user_id
            ).first()
            
            if existing:
                results["skipped"] += 1
                continue
            
            try:
                self.generate_user_embedding(user.user_id, db)
                results["success"] += 1
            except Exception as e:
                print(f"Failed to generate embedding for user {user.user_id}: {e}")
                results["failed"] += 1
        
        return results
    
    def generate_all_opportunity_embeddings(self, db: Session) -> dict:
        """
        Generate embeddings for all opportunities that don't have them.
        
        Args:
            db: Database session
            
        Returns:
            Dict with success/failure counts
        """
        opportunities = db.query(Opportunity).all()
        
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        for opp in opportunities:
            # Check if already has embedding
            existing = db.query(OpportunityEmbedding).filter(
                OpportunityEmbedding.opportunity_id == opp.opportunity_id
            ).first()
            
            if existing:
                results["skipped"] += 1
                continue
            
            try:
                self.generate_opportunity_embedding(opp.opportunity_id, db)
                results["success"] += 1
            except Exception as e:
                print(f"Failed to generate embedding for opportunity {opp.opportunity_id}: {e}")
                results["failed"] += 1
        
        return results

