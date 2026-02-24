"""
API endpoints for triggering the UCLA CS lab scraper.
"""

import sys
from pathlib import Path

from fastapi import APIRouter

# Ensure backend dir is on path so scrape_ucla can be imported
_backend = Path(__file__).resolve().parent.parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

try:
    from scrape_ucla import run_ucla_scrape
except ImportError:
    run_ucla_scrape = None


router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.post("/run")
def run_scrape():
    """
    Run the UCLA CS lab scraper (BFS crawl + GPT-4o extraction + DB insert).
    No auth for demo. Returns when complete.
    """
    if run_ucla_scrape is None:
        return {
            "status": "error",
            "message": "Scraper not available (run server from backend directory).",
            "opportunities_added": 0,
        }
    opportunities_added = run_ucla_scrape()
    return {
        "status": "complete",
        "opportunities_added": opportunities_added,
    }
