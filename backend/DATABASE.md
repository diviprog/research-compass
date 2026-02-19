# Database Management Guide

## Quick Start

### Initialize Database (First Time)
```bash
cd backend
python init_db.py
```

This creates the `data/research_assistant.db` SQLite file with all tables.

---

## Database Migrations with Alembic

### Setup (First Time Only)
Alembic is already configured! The structure is:
```
backend/
├── alembic/
│   ├── versions/        # Migration scripts go here
│   ├── env.py          # Migration environment
│   └── script.py.mako  # Template for new migrations
├── alembic.ini          # Alembic configuration
```

### Common Migration Commands

#### 1. Create Initial Migration (After models are defined)
```bash
alembic revision --autogenerate -m "Initial migration"
```

#### 2. Apply Migrations (Upgrade to Latest)
```bash
alembic upgrade head
```

#### 3. Downgrade (Rollback One Version)
```bash
alembic downgrade -1
```

#### 4. Check Current Migration Status
```bash
alembic current
```

#### 5. View Migration History
```bash
alembic history
```

#### 6. Create Custom Migration (Manual)
```bash
alembic revision -m "add new column"
```

---

## Database Schema

### Tables

#### **users**
- `user_id` (PK) - Integer, auto-increment
- `email` - String(255), unique, indexed
- `name` - String(255)
- `research_interests` - Text
- `preferred_methods` - JSON array
- `preferred_datasets` - JSON array
- `experience_level` - String(50)
- `location_preferences` - JSON array
- `availability` - String(100)
- `created_at` - DateTime
- `updated_at` - DateTime

#### **opportunities**
- `opportunity_id` (PK) - Integer, auto-increment
- `source_url` - String(1000), unique, indexed
- `scraped_at` - DateTime
- `last_updated` - DateTime
- `title` - String(500), indexed
- `description` - Text
- `lab_name` - String(255), indexed
- `pi_name` - String(255), indexed
- `institution` - String(255), indexed
- `research_topics` - JSON array
- `methods` - JSON array
- `datasets` - JSON array
- `deadline` - DateTime, nullable, indexed
- `funding_status` - String(100)
- `experience_required` - String(100)
- `contact_email` - String(255)
- `application_link` - String(1000)
- `is_active` - Boolean (default True)

#### **matches**
- `match_id` (PK) - Integer, auto-increment
- `user_id` (FK) - Integer → users.user_id
- `opportunity_id` (FK) - Integer → opportunities.opportunity_id
- `match_score` - Float (0-1), indexed
- `fit_rationale` - Text
- `user_status` - String(50), indexed (saved/dismissed/contacted/pending)
- `created_at` - DateTime, indexed
- `updated_at` - DateTime

#### **outreach**
- `outreach_id` (PK) - Integer, auto-increment
- `user_id` (FK) - Integer → users.user_id
- `opportunity_id` (FK) - Integer → opportunities.opportunity_id
- `generated_email` - Text
- `user_edited_email` - Text, nullable
- `sent_at` - DateTime, nullable, indexed
- `response_received` - Boolean (default False)
- `response_text` - Text, nullable
- `created_at` - DateTime, indexed
- `updated_at` - DateTime

---

## Usage Examples

### Using Models in Python

```python
from app.db import SessionLocal, init_db
from app.models import User, Opportunity, Match, Outreach

# Initialize database (first time)
init_db()

# Create a session
db = SessionLocal()

# Create a user
user = User(
    email="alex@example.com",
    name="Alex Chen",
    research_interests="Computer vision and NLP",
    preferred_methods=["Deep Learning", "Transformers"],
    preferred_datasets=["COCO", "ImageNet"],
    experience_level="undergraduate",
    location_preferences=["Boston", "Remote"],
    availability="part-time"
)
db.add(user)
db.commit()
db.refresh(user)

# Query users
users = db.query(User).filter(User.experience_level == "undergraduate").all()

# Create an opportunity
opp = Opportunity(
    source_url="https://mit.edu/lab/position",
    title="Research Assistant - Vision Lab",
    description="Work on multimodal learning",
    lab_name="Vision Lab",
    pi_name="Dr. Smith",
    institution="MIT",
    research_topics=["Computer Vision", "NLP"],
    methods=["Deep Learning"],
    datasets=["COCO"],
    funding_status="funded",
    is_active=True
)
db.add(opp)
db.commit()

# Create a match
match = Match(
    user_id=user.user_id,
    opportunity_id=opp.opportunity_id,
    match_score=0.85,
    fit_rationale="Strong overlap in CV and NLP interests",
    user_status="pending"
)
db.add(match)
db.commit()

# Query with relationships
user_with_matches = db.query(User).filter(User.user_id == 1).first()
for match in user_with_matches.matches:
    print(f"Matched with: {match.opportunity.title}")

# Close session
db.close()
```

---

## Switching to PostgreSQL (Production)

### 1. Install PostgreSQL Driver
```bash
pip install psycopg2-binary
```

### 2. Set DATABASE_URL Environment Variable
```bash
# In .env file
DATABASE_URL=postgresql://user:password@localhost:5432/research_assistant
```

### 3. Run Migrations
```bash
alembic upgrade head
```

That's it! SQLAlchemy models work with both SQLite and PostgreSQL.

---

## Troubleshooting

### Reset Database (Deletes All Data!)
```python
from app.db import reset_db
reset_db()
```

### Check Database File Location
```python
from app.db import database
print(database.DATABASE_PATH)
# Output: /path/to/backend/data/research_assistant.db
```

### Manual SQL Access
```bash
sqlite3 backend/data/research_assistant.db
```

```sql
.tables
.schema users
SELECT * FROM users;
.quit
```

---

## Environment Variables

Set these in `.env` file in backend directory:

```env
# Database
DATABASE_URL=sqlite:///./data/research_assistant.db
DATABASE_ECHO=false  # Set to true to see SQL queries

# For PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

