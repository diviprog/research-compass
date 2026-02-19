"""
Test script for semantic search functionality.

This demonstrates the complete search flow:
1. Create test opportunities
2. Generate embeddings
3. Search using natural language
"""

import os
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/research_compass")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

from app.models.opportunity import Opportunity
from app.services.embeddings import EmbeddingService

def create_sample_opportunities(db):
    """Create sample opportunities for testing."""
    print("📝 Creating sample opportunities...\n")
    
    opportunities = [
        {
            "title": "Machine Learning Research Assistant - Medical Imaging",
            "description": "Work on developing deep learning models for analyzing MRI and CT scans. We use convolutional neural networks and transformers to detect tumors and other abnormalities. Experience with PyTorch or TensorFlow preferred.",
            "lab_name": "Medical AI Lab",
            "pi_name": "Dr. Sarah Chen",
            "institution": "Stanford University",
            "research_topics": ["Computer Vision", "Medical Imaging", "Deep Learning"],
            "location_city": "Stanford",
            "location_state": "CA",
            "is_remote": False,
            "degree_levels": ["undergraduate", "masters"],
            "paid_type": "stipend",
            "min_hours": 10,
            "max_hours": 20,
            "source_url": "https://example.com/opp1",
            "is_active": True
        },
        {
            "title": "Climate Change Data Analysis",
            "description": "Analyze satellite data and climate models to understand global warming trends. Use statistical methods and machine learning to predict future climate scenarios. Python and R experience required.",
            "lab_name": "Climate Science Lab",
            "pi_name": "Dr. James Rodriguez",
            "institution": "MIT",
            "research_topics": ["Climate Science", "Data Analysis", "Machine Learning"],
            "location_city": "Cambridge",
            "location_state": "MA",
            "is_remote": True,
            "degree_levels": ["undergraduate", "masters", "phd"],
            "paid_type": "hourly",
            "min_hours": 15,
            "max_hours": 25,
            "source_url": "https://example.com/opp2",
            "is_active": True
        },
        {
            "title": "Natural Language Processing Research",
            "description": "Work on large language models and transformers for text understanding. Focus on question answering and information retrieval. Experience with BERT, GPT, or similar models helpful.",
            "lab_name": "NLP Lab",
            "pi_name": "Dr. Emily Zhang",
            "institution": "UC Berkeley",
            "research_topics": ["NLP", "Machine Learning", "AI"],
            "location_city": "Berkeley",
            "location_state": "CA",
            "is_remote": False,
            "degree_levels": ["masters", "phd"],
            "paid_type": "stipend",
            "min_hours": 20,
            "max_hours": 40,
            "source_url": "https://example.com/opp3",
            "is_active": True
        }
    ]
    
    created = []
    for opp_data in opportunities:
        # Check if already exists
        existing = db.query(Opportunity).filter(
            Opportunity.source_url == opp_data["source_url"]
        ).first()
        
        if existing:
            print(f"   ⏭️  Skipped: {opp_data['title']} (already exists)")
            created.append(existing)
        else:
            opp = Opportunity(**opp_data)
            db.add(opp)
            db.commit()
            db.refresh(opp)
            created.append(opp)
            print(f"   ✅ Created: {opp_data['title']}")
    
    return created

def generate_embeddings_for_opportunities(opportunities, db):
    """Generate embeddings for all opportunities."""
    print("\n🧠 Generating embeddings...\n")
    
    service = EmbeddingService()
    
    for opp in opportunities:
        try:
            service.generate_opportunity_embedding(opp.opportunity_id, db)
            print(f"   ✅ Embedded: {opp.title[:50]}...")
        except Exception as e:
            print(f"   ❌ Failed: {opp.title[:50]}... - {e}")

def test_search():
    """Test the search functionality."""
    print("\n" + "="*70)
    print("🔍 TESTING SEMANTIC SEARCH")
    print("="*70 + "\n")
    
    db = SessionLocal()
    
    try:
        # Step 1: Create sample opportunities
        opportunities = create_sample_opportunities(db)
        
        # Step 2: Generate embeddings
        generate_embeddings_for_opportunities(opportunities, db)
        
        # Step 3: Test search
        print("\n" + "="*70)
        print("🎯 SEARCH RESULTS")
        print("="*70 + "\n")
        
        test_queries = [
            "I want to work on AI for medical diagnosis",
            "Interested in climate change and environmental science",
            "Natural language processing and transformers"
        ]
        
        from app.services.search import SearchService
        search_service = SearchService()
        
        for query in test_queries:
            print(f"Query: \"{query}\"\n")
            
            results = search_service.search_opportunities(
                query=query,
                filters=None,
                limit=3,
                db=db
            )
            
            for i, (opp, similarity) in enumerate(results, 1):
                print(f"  {i}. {opp.title}")
                print(f"     Institution: {opp.institution}")
                print(f"     Similarity: {similarity:.3f}")
                print(f"     Location: {opp.location_city}, {opp.location_state}")
                print()
            
            print("-" * 70 + "\n")
        
        print("✅ Search test completed successfully!\n")
        print("🚀 You can now use the API:")
        print("   POST http://localhost:8000/api/opportunities/search")
        print('   Body: {"query": "your research interests here", "limit": 20}\n')
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_search()

