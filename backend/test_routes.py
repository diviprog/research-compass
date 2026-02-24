#!/usr/bin/env python3
"""
Quick script to test API routes. Run with the server up: python run.py (in another terminal).

Usage:
    python test_routes.py

Set BASE_URL if your API is not at http://localhost:8000.
"""

import os
import sys

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API = f"{BASE_URL}/api"

def ok(name, r):
    status = "✓" if r.status_code in (200, 201, 204) else "✗"
    print(f"  {status} {name}: {r.status_code}")

def test_routes():
    print(f"Testing API at {BASE_URL}\n")

    # 1. Health (no auth) — longer timeout for cold server start
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=15)
    except requests.exceptions.ConnectionError:
        print("  ✗ Connection refused. Start the server first in another terminal:")
        print("      cd backend && python run.py")
        print("  Then run this script again.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("  ✗ Request timed out. Is the server starting up? Try again in a few seconds.")
        sys.exit(1)

    ok("GET /health", r)
    if r.status_code != 200:
        print("  Server not responding. Is it running? (python run.py)")
        return

    # 2. Root
    r = requests.get(BASE_URL, timeout=5)
    ok("GET /", r)

    # 3. Sign up (password must have upper, lower, and digit per API validation)
    r = requests.post(
        f"{API}/auth/signup",
        json={"email": "test_routes@example.com", "password": "Testpass1", "name": "Test User"},
        timeout=10,
    )
    ok("POST /api/auth/signup", r)
    if r.status_code not in (200, 201):
        # Maybe already registered — try sign in with same password
        r = requests.post(
            f"{API}/auth/signin",
            json={"email": "test_routes@example.com", "password": "Testpass1"},
            timeout=10,
        )
        ok("POST /api/auth/signin (existing user)", r)

    if r.status_code not in (200, 201):
        print("  Auth failed; skipping protected routes.")
        return

    data = r.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    if not access_token:
        print("  No access_token in response.")
        return

    headers = {"Authorization": f"Bearer {access_token}"}

    # 4. Current user
    r = requests.get(f"{API}/auth/me", headers=headers, timeout=5)
    ok("GET /api/auth/me", r)
    user_id = r.json().get("user_id") if r.status_code == 200 else None

    # 5. Opportunities list (requires auth)
    r = requests.get(f"{API}/opportunities?limit=5", headers=headers, timeout=5)
    ok("GET /api/opportunities", r)
    opportunities = r.json() if r.status_code == 200 and isinstance(r.json(), list) else []
    if opportunities:
        print(f"      -> {len(opportunities)} opportunities returned")

    # 6. Get one opportunity by ID (essential for dashboard detail view)
    if opportunities:
        first_id = opportunities[0].get("opportunity_id")
        if first_id is not None:
            r = requests.get(f"{API}/opportunities/{first_id}", headers=headers, timeout=5)
            ok("GET /api/opportunities/{id}", r)

    # 7. Profile (get)
    r = requests.get(f"{API}/profile", headers=headers, timeout=5)
    ok("GET /api/profile", r)

    # 8. Profile create/update (essential for onboarding)
    r = requests.post(
        f"{API}/profile",
        headers=headers,
        json={
            "university": "Test University",
            "major": "Computer Science",
            "graduation_year": 2026,
            "research_interests": "Machine learning and natural language processing.",
            "experience_level": "undergraduate",
        },
        timeout=10,
    )
    ok("POST /api/profile", r)

    # 9. Profile partial update
    r = requests.patch(
        f"{API}/profile",
        headers=headers,
        json={"availability": "part-time"},
        timeout=5,
    )
    ok("PATCH /api/profile", r)

    # 10. Get profile by user_id
    if user_id is not None:
        r = requests.get(f"{API}/profile/{user_id}", headers=headers, timeout=5)
        ok("GET /api/profile/{user_id}", r)

    # 11. Token refresh (essential for session longevity)
    if refresh_token:
        r = requests.post(
            f"{API}/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=5,
        )
        ok("POST /api/auth/refresh", r)
        if r.status_code == 200:
            data = r.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")  # new token; old one is revoked
            headers = {"Authorization": f"Bearer {access_token}"}

    # 12. Embeddings stats (readiness check; may 500 on SQLite if embedding tables missing)
    r = requests.get(f"{API}/embeddings/stats", timeout=5)
    ok("GET /api/embeddings/stats", r)

    # 13. Logout (revoke refresh token; use current refresh_token from refresh response if we refreshed)
    if refresh_token:
        r = requests.post(
            f"{API}/auth/logout",
            headers=headers,
            json={"refresh_token": refresh_token},
            timeout=5,
        )
        ok("POST /api/auth/logout", r)

    # 14. Search test endpoint (no auth)
    r = requests.get(f"{API}/opportunities/search/test", timeout=5)
    ok("GET /api/opportunities/search/test", r)
    if r.status_code == 200:
        d = r.json()
        print(f"      -> ready={d.get('ready')}, opportunities_with_embeddings={d.get('opportunities_with_embeddings', 'N/A')}")

    print("\nDone. Open http://localhost:8000/docs for interactive Swagger UI.")

if __name__ == "__main__":
    test_routes()
