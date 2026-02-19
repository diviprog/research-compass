#!/usr/bin/env python3
"""
Database initialization script.

Run this script to create all database tables.

Usage:
    python init_db.py
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization complete!")

