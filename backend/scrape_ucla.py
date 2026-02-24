#!/usr/bin/env python3
"""
UCLA CS research labs scraper: extract professor names → find pages via DuckDuckGo → GPT-4o extraction → DB.
Run from backend directory: python scrape_ucla.py
"""

import json
import os
import re
import sys
import time
import warnings

import requests
from bs4 import BeautifulSoup
with warnings.catch_warnings():
    warnings.simplefilter("ignore", RuntimeWarning)
    from duckduckgo_search import DDGS
from openai import OpenAI

if __name__ == "__main__":
    _backend_dir = os.path.dirname(os.path.abspath(__file__))
    if _backend_dir not in sys.path:
        sys.path.insert(0, _backend_dir)

from app.db.database import SessionLocal
from app.models.opportunity import Opportunity

START_URL = "https://www.cs.ucla.edu/research-labs/"
MAX_TEXT_CHARS = 3000
SEARCH_DELAY_SECONDS = 1
REQUEST_TIMEOUT = 10

GPT_PROMPT = """Given this UCLA CS professor's webpage, create a research opportunity record.
Return a single JSON object with these fields:
- title: "Research with Prof. [Last Name] – [their main research area, max 5 words]". If you cannot determine the professor's last name, use "Professor" (e.g. "Research with Professor – [area]").
- description: 3-4 sentences describing their research and what a student working with them would work on. Be specific about methods and topics.
- pi_name: professor's full name
- lab_name: their lab name, or "Professor Lab" if not found
- research_topics: array of 4-6 specific keyword topics from their research
- contact_email: email address if found on the page, else null
- degree_levels: ["undergraduate", "masters", "phd"]
- is_funded: true
Return ONLY a valid JSON object. If the page has no research content, return null."""


def _is_professor_name(part: str) -> bool:
    """True if part looks like a professor name (for blocklist and regex)."""
    if not part or len(part) < 4 or len(part) > 60:
        return False
    if part.lower() == "multiple faculty":
        return False
    lower = part.lower()
    if any(lower == w or lower.endswith(" " + w) for w in (
        "lab", "phd", "group", "giving", "wireless", "networking", "alumni"
    )):
        return False
    if "group" in lower or "lab" in lower:
        return False
    return bool(re.match(r"^[A-Z][a-z]+(?:\s+[A-Za-z][a-z\.]*)*$", part))


def _extract_professor_names(html: str) -> list[str]:
    """Extract professor/faculty names from the research-labs page (in parentheses next to lab names)."""
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    names = set()
    for m in re.finditer(r"\(([^)]+)\)", text):
        inner = m.group(1).strip()
        if "multiple faculty" in inner.lower() and "," not in inner:
            continue
        if inner.lower() in ("alumni", "lab", "phd", "prof"):
            continue
        for part in re.split(r"\s*,\s*", inner):
            part = part.strip()
            if _is_professor_name(part):
                names.add(part)
    return sorted(names)


def _extract_professor_urls_from_labs_page(html: str) -> dict[str, str]:
    """Parse research-labs page: for each professor name, get the lab/faculty URL from the same list item."""
    soup = BeautifulSoup(html, "lxml")
    name_to_url: dict[str, str] = {}
    for li in soup.find_all("li"):
        links = li.find_all("a", href=True)
        if not links:
            continue
        # All hrefs in this li (lab link or professor link)
        hrefs = [a["href"].strip() for a in links if a.get("href", "").strip()]
        if not hrefs:
            continue
        text = li.get_text()
        # Find (Name) or (Name1, Name2) in this li
        for m in re.finditer(r"\(([^)]+)\)", text):
            inner = m.group(1).strip()
            if "multiple faculty" in inner.lower() and "," not in inner:
                continue
            if inner.lower() in ("alumni", "lab", "phd", "prof"):
                continue
            for part in re.split(r"\s*,\s*", inner):
                part = part.strip()
                if not _is_professor_name(part):
                    continue
                # If this name is the link text of an <a>, use that link's href
                url_for_name = None
                for a in links:
                    if a.get("href") and (a.get_text() or "").strip() == part:
                        url_for_name = a["href"].strip()
                        break
                if url_for_name:
                    name_to_url[part] = url_for_name
                else:
                    # Use first (lab) link in the li for this name
                    name_to_url[part] = hrefs[0]
    return name_to_url


def _find_professor_page(professor_name: str) -> str | None:
    """DuckDuckGo search for professor's UCLA research page. Prefer site:ucla.edu; then first ucla.edu in top 5, else first result."""
    def _search(q: str) -> list:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                ddgs = DDGS()
                return list(ddgs.text(q, max_results=5))
        except Exception:
            return []

    def _url(r: dict) -> str:
        return (r.get("href") or r.get("link") or "").strip()

    # Prefer UCLA pages: first try with site:ucla.edu
    site_query = f'"{professor_name}" site:ucla.edu computer science research'
    results = _search(site_query)
    for r in results:
        href = _url(r)
        if href and "ucla.edu" in href:
            return href
    if results and _url(results[0]):
        return _url(results[0])

    # Fallback: general search
    query = f'"{professor_name}" UCLA computer science research'
    results = _search(query)
    for r in results:
        href = _url(r)
        if href and "ucla.edu" in href:
            return href
    if results:
        return _url(results[0]) or None
    return None


def _fetch_page(url: str) -> str | None:
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            return None
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except Exception:
        return None


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text[:MAX_TEXT_CHARS]


def _extract_opportunity_with_gpt(page_text: str, client: OpenAI) -> dict | None:
    """Send page text to GPT-4o; return single opportunity dict or None."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": GPT_PROMPT},
                {"role": "user", "content": page_text},
            ],
            max_tokens=1500,
        )
        raw = (response.choices[0].message.content or "").strip()
        if not raw or raw.lower() == "null":
            return None
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)
        if isinstance(data, dict) and data.get("title") and data.get("description"):
            return data
        return None
    except (json.JSONDecodeError, Exception):
        return None


def run_ucla_scrape() -> int:
    """
    Step 1: Extract professor names from research-labs page.
    Step 2: For each professor, find research page via DuckDuckGo.
    Step 3: Scrape page, extract opportunity with GPT-4o.
    Step 4: Truncate opportunities table, insert each, generate embedding.
    Step 5: Print summary.
    Returns number of opportunities inserted.
    """
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set; cannot run GPT extraction.")
        return 0

    client = OpenAI(api_key=api_key)
    db = SessionLocal()

    try:
        # ——— Step 4 (early): Clear ALL existing opportunities ———
        deleted = db.query(Opportunity).delete()
        db.commit()
        print(f"Cleared {deleted} existing opportunity/opportunities.\n")

        # ——— Step 1: Fetch research-labs page; extract professor names and URLs from it ———
        print("Step 1 — Fetching research-labs page and extracting professor names + URLs...")
        html = _fetch_page(START_URL)
        if not html:
            print("Failed to fetch research-labs page.")
            return 0
        professor_names = _extract_professor_names(html)
        name_to_url = _extract_professor_urls_from_labs_page(html)
        print(f"Found {len(professor_names)} professor(s), {len(name_to_url)} with URLs from page.")
        for n in professor_names:
            print(f"  - {n}")
        print()

        if not professor_names:
            print("No professor names extracted. Exiting.")
            return 0

        # Embedding service (may fail on SQLite if embedding tables don't exist)
        try:
            from app.services.embeddings import EmbeddingService
            embedding_service = EmbeddingService()
        except Exception:
            embedding_service = None

        inserted = 0

        for i, name in enumerate(professor_names):
            # ——— Step 2: Get professor page URL (from research-labs page first, else DuckDuckGo) ———
            url = name_to_url.get(name)
            if not url:
                if i > 0:
                    time.sleep(SEARCH_DELAY_SECONDS)
                url = _find_professor_page(name)
            if not url:
                print(f"  {name} → (no URL found) → skipped")
                continue

            # ——— Step 3: Scrape and extract with GPT-4o ———
            page_html = _fetch_page(url)
            if not page_html:
                print(f"  {name} → {url} → (fetch failed) → skipped")
                continue
            text = _extract_text(page_html)
            if not text.strip():
                print(f"  {name} → {url} → (no text) → skipped")
                continue
            opp_data = _extract_opportunity_with_gpt(text, client)
            if not opp_data:
                print(f"  {name} → {url} → (GPT returned null/invalid) → skipped")
                continue

            topics = opp_data.get("research_topics") or []
            topics_str = ", ".join(topics[:4]) if topics else "—"

            # ——— Step 4: Insert into DB ———
            title = (opp_data.get("title") or "").strip()
            description = (opp_data.get("description") or "").strip()
            if not title or not description:
                print(f"  {name} → {url} → {topics_str} → skipped (missing title/description)")
                continue

            # Ensure unique source_url (model has unique constraint)
            source_url = url.split("#")[0].rstrip("/")
            if db.query(Opportunity).filter(Opportunity.source_url == source_url).first():
                source_url = f"{source_url}#{name.replace(' ', '-')}"

            record = Opportunity(
                source_url=source_url,
                title=title,
                description=description,
                lab_name=(opp_data.get("lab_name") or "").strip() or None,
                pi_name=(opp_data.get("pi_name") or "").strip() or None,
                institution="UCLA",
                research_topics=opp_data.get("research_topics") if isinstance(opp_data.get("research_topics"), list) else None,
                methods=None,
                datasets=None,
                deadline=None,
                funding_status="funded" if opp_data.get("is_funded") else "unfunded",
                experience_required=None,
                contact_email=(opp_data.get("contact_email") or "").strip() or None,
                application_link=source_url,
                is_active=True,
                location_city="Los Angeles",
                location_state="CA",
                is_remote=False,
                degree_levels=opp_data.get("degree_levels") if isinstance(opp_data.get("degree_levels"), list) else ["undergraduate", "masters", "phd"],
                min_hours=None,
                max_hours=None,
                paid_type="stipend",
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            inserted += 1

            if embedding_service:
                try:
                    embedding_service.generate_opportunity_embedding(record.opportunity_id, db)
                except Exception:
                    pass

            print(f"  {name} → {url} → {topics_str} → inserted")

        # ——— Step 5: Summary ———
        print()
        print("——— Summary ———")
        print(f"Total professors found: {len(professor_names)}")
        print(f"Total successfully inserted: {inserted}")
        return inserted

    finally:
        db.close()


if __name__ == "__main__":
    print("UCLA CS research labs scraper (professor names → DuckDuckGo → GPT-4o → DB)")
    print("Start URL:", START_URL)
    print()
    added = run_ucla_scrape()
    print()
    print(f"Done. Opportunities added: {added}")
