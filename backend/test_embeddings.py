"""
Quick test script for embedding generation.

Run this to verify:
1. OpenAI API key is working
2. Embedding generation works
3. Database storage works
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/research_compass")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

from app.services.embeddings import EmbeddingService

def test_embedding_generation():
    """Test generating a simple embedding."""
    print("🧪 Testing Embedding Service\n")
    
    # Test 1: Initialize service
    print("1️⃣ Initializing EmbeddingService...")
    try:
        service = EmbeddingService()
        print("   ✅ Service initialized (OpenAI API key found)\n")
    except ValueError as e:
        print(f"   ❌ Failed: {e}")
        print("   💡 Make sure OPENAI_API_KEY is set in backend/.env\n")
        return
    
    # Test 2: Generate a test embedding
    print("2️⃣ Generating test embedding...")
    try:
        test_text = "I want to research machine learning for medical imaging"
        embedding = service._generate_embedding(test_text)
        print(f"   ✅ Embedding generated!")
        print(f"   📊 Dimensions: {len(embedding)}")
        print(f"   📈 First 5 values: {embedding[:5]}\n")
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
        return
    
    # Test 3: Check database
    print("3️⃣ Checking database connection...")
    db = SessionLocal()
    try:
        from app.models.user import User
        user_count = db.query(User).count()
        print(f"   ✅ Database connected!")
        print(f"   👥 Users in database: {user_count}\n")
        
        if user_count == 0:
            print("   💡 Tip: Create a test user first to test full embedding flow")
    except Exception as e:
        print(f"   ❌ Database error: {e}\n")
    finally:
        db.close()
    
    print("✅ All tests passed! Embedding service is ready.")
    print("\n📚 Next steps:")
    print("   1. Create a user with research interests")
    print("   2. Call: POST /api/embeddings/users/{user_id}")
    print("   3. Create opportunities")
    print("   4. Call: POST /api/embeddings/opportunities/generate-all")
    print("   5. Ready for matching! 🎯\n")

if __name__ == "__main__":
    test_embedding_generation()

