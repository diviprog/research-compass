"""
API endpoints for generating and managing outreach emails.
"""

import os
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from openai import OpenAI
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.opportunity import Opportunity
from app.models.outreach import Outreach
from app.models.user import User


router = APIRouter(prefix="/outreach", tags=["outreach"])


class GenerateOutreachRequest(BaseModel):
    """Request body for generating an outreach email."""
    opportunity_id: int = Field(..., description="ID of the research opportunity")
    additional_context: Optional[str] = Field(None, description="Optional extra context for the email")


def _parse_subject_and_body(text: str) -> tuple[str, str]:
    """Parse 'Subject: ...\\n\\n<body>' into (subject, body). Falls back to full text as body if no Subject line."""
    subject_match = re.match(r"^\s*Subject:\s*(.+?)(?:\n\n|\n\s*\n)", text, re.IGNORECASE | re.DOTALL)
    if subject_match:
        subject = subject_match.group(1).strip()
        body = text[subject_match.end() :].strip()
        return subject, body
    lines = text.strip().split("\n")
    if lines and lines[0].lower().startswith("subject:"):
        subject = lines[0].split(":", 1)[1].strip()
        body = "\n".join(lines[1:]).strip()
        return subject, body
    return "", text.strip()


@router.post("/generate")
def generate_outreach(
    request: GenerateOutreachRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a personalized cold academic email for a research opportunity.
    Requires JWT auth. Uses the current user's profile and the opportunity details.
    """
    # Fetch opportunity (404 if not found)
    opportunity = db.query(Opportunity).filter(
        Opportunity.opportunity_id == request.opportunity_id,
        Opportunity.is_active == True,
    ).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )

    # Require profile with research interests (400 if missing)
    if not current_user.research_interests or not current_user.research_interests.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile incomplete: add your research interests to generate outreach emails.",
        )

    # OpenAI client (reuse same env as rest of codebase)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured",
        )
    client = OpenAI(api_key=api_key)

    # Student background: research_interests holds the research summary narrative (from resume parse or manual entry)
    research_summary = current_user.research_interests.strip()
    student_name = current_user.name or "The applicant"
    student_email = current_user.email or ""
    student_university = current_user.university or "UCLA"
    student_major = current_user.major or ""
    student_graduation_year = current_user.graduation_year or ""

    pi_name = opportunity.pi_name or "the PI"
    lab_name = opportunity.lab_name or "the lab"
    institution = opportunity.institution or "the institution"
    research_topics = ", ".join(opportunity.research_topics) if opportunity.research_topics else "their research"
    description = (opportunity.description or "").strip() or "No additional description."

    additional = f"\nAdditional context the applicant asked to include: {request.additional_context}" if request.additional_context else ""

    prompt = f"""You are helping a student write a cold email to a professor to inquire about research opportunities.

Student background:
Student name: {student_name}
Student email: {student_email}
University: {student_university}
Major: {student_major}
Graduation year: {student_graduation_year}

Research summary:
{research_summary}
{additional}

Professor/Lab details:
- PI: {pi_name}
- Lab: {lab_name}
- Institution: {institution}
- Research topics: {research_topics}
- Lab description: {description}

Write a cold academic email from the student to this professor. Requirements:
- 150-200 words total
- Start with a specific connection between the student's past work and the professor's research topics
- Mention 1-2 specific projects or methods from the student's background that are relevant
- Ask specifically about undergraduate/graduate research opportunities
- Professional but not stiff — genuine and direct
- End with a clear ask and contact offer
- Sign the email with the student's actual name, email, and university — do not use placeholders.
- Output format: first line is Subject: [subject line], then a blank line, then the email body"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        raw_content = (response.choices[0].message.content or "").strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OpenAI request failed: {str(e)}",
        )

    subject, body = _parse_subject_and_body(raw_content)
    if not body:
        body = raw_content
    if not subject:
        user_name = current_user.name or "Student"
        subject = f"Research opportunity inquiry – {user_name}"

    # Store full email in Outreach (same format for reference)
    generated_email = f"Subject: {subject}\n\n{body}"

    outreach = Outreach(
        user_id=current_user.user_id,
        opportunity_id=opportunity.opportunity_id,
        generated_email=generated_email,
    )
    db.add(outreach)
    db.commit()
    db.refresh(outreach)

    return {
        "subject": subject,
        "body": body,
        "opportunity_id": opportunity.opportunity_id,
        "outreach_id": outreach.outreach_id,
    }
