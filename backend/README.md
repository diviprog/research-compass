# Research Assistant Backend API

FastAPI backend for the AI-powered research opportunity discovery platform.

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the backend directory:

```bash
# Copy from your root .env or create new
cp ../.env .env

# Or create manually with:
DATABASE_URL=sqlite:///./data/research_assistant.db
DATABASE_ECHO=false
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### 3. Initialize Database

```bash
python init_db.py
```

### 4. Run the Server

**Option A: Simple script**
```bash
python run.py
```

**Option B: Using uvicorn directly**
```bash
uvicorn app.main:app --reload --port 8000
```

**Option C: From app.main**
```bash
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas (for API validation)
│   ├── api/                 # API route handlers
│   ├── agents/              # Multi-agent system
│   ├── core/                # Configuration
│   └── db/                  # Database setup
├── tests/                   # Test suite
├── alembic/                 # Database migrations
├── data/                    # SQLite database location
└── run.py                   # Server run script
```

---

## API Endpoints

### Current Endpoints

- `GET /` - Root endpoint, API info
- `GET /health` - Health check

### Coming Soon

- `POST /api/profile` - Create/update user profile
- `GET /api/profile/{user_id}` - Get user profile
- `POST /api/discover` - Trigger discovery pipeline
- `GET /api/opportunities` - List opportunities
- `GET /api/matches/{user_id}` - Get user matches
- `POST /api/outreach/generate` - Generate outreach email

---

## Development

### Run Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

See [TESTING.md](TESTING.md) for detailed testing guide.

### Database Management

```bash
# Initialize database
python init_db.py

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

See [DATABASE.md](DATABASE.md) for detailed database guide.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./data/research_assistant.db` |
| `DATABASE_ECHO` | Log SQL queries | `false` |
| `DEBUG` | Enable debug mode | `false` |
| `ANTHROPIC_API_KEY` | Claude API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GOOGLE_API_KEY` | Google (Gemini) API key | - |
| `BRIGHT_DATA_API_KEY` | Web scraping API key | - |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:5173"]` |

---

## Production Deployment

### Switch to PostgreSQL

1. Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

2. Update DATABASE_URL:
```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

3. Run migrations:
```bash
alembic upgrade head
```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Troubleshooting

### Import Errors

Make sure you're running from the backend directory:
```bash
cd backend
python run.py
```

### Database Locked

If using SQLite and getting locked errors:
```bash
# Reset the database
python init_db.py
```

### Port Already in Use

Change the port in `run.py` or use:
```bash
uvicorn app.main:app --reload --port 8001
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [DATABASE.md](DATABASE.md) - Database guide
- [TESTING.md](TESTING.md) - Testing guide

