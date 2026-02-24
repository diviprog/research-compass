"""
Student Profile API endpoints for creating and managing student profiles.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.core.auth import get_current_user
from app.utils.resume_parser import parse_resume

router = APIRouter(prefix="/profile", tags=["Profile"])

# Configure upload directory
UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload-resume", status_code=status.HTTP_200_OK)
async def upload_and_parse_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a resume PDF and parse it to extract structured information.

    This endpoint accepts a PDF file, saves it, and uses an open-source parser
    to extract:
    - Personal information (email, phone)
    - Education (university, major, GPA, graduation year)
    - Skills (technical skills)
    - Work/Research experiences

    The parsed data is returned as JSON for the user to review/edit before
    submitting their profile.

    - Requires valid access token in Authorization header
    - Accepts PDF files only (max 10MB)

    Returns:
        Dictionary with parsed resume data

    Raises:
        HTTPException 400: If file is not a PDF or exceeds size limit
        HTTPException 500: If parsing fails
    """
    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted"
        )

    # Validate file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resume_{current_user.user_id}_{timestamp}.pdf"
    file_path = UPLOAD_DIR / filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Parse resume - gracefully handle partial failures
    empty_parsed = {
        "skills": [],
        "education": {"university": None, "major": None, "graduation_year": None},
        "research_summary": None,
        "raw_text": "",
    }
    try:
        parsed_data = parse_resume(str(file_path))

        # Update user's resume_file_path
        current_user.resume_file_path = str(file_path)

        # PATCH-style auto-update profile: only overwrite where parsed value is non-null
        if parsed_data.get("research_summary"):
            current_user.research_interests = parsed_data["research_summary"]
        education = parsed_data.get("education") or {}
        if education.get("university") is not None:
            current_user.university = education["university"]
        if education.get("major") is not None:
            current_user.major = education["major"]
        if education.get("graduation_year") is not None:
            current_user.graduation_year = education["graduation_year"]

        db.commit()

        return {
            "message": "Resume uploaded and profile updated",
            "file_path": str(file_path),
            "parsed_data": parsed_data,
            "parsing_status": "success" if parsed_data.get("research_summary") else "partial",
            "note": "Profile auto-updated with research summary and education where available. Review on Profile page and Save if needed.",
        }

    except Exception as e:
        current_user.resume_file_path = str(file_path)
        db.commit()
        return {
            "message": "Resume uploaded but parsing had issues - please fill in your information manually",
            "file_path": str(file_path),
            "parsed_data": empty_parsed,
            "parsing_status": "failed",
            "error": str(e),
            "note": "Your resume is saved. You can enter your information manually on the Profile page.",
        }


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def create_or_update_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update the student profile for the authenticated user.

    This endpoint allows students to set up their complete profile after signup,
    including university information, past experiences, skills, and research interests.

    - Requires valid access token in Authorization header
    - All profile data will be stored in the user record

    Returns:
        ProfileResponse with complete profile data

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 422: If validation fails
    """
    # Convert Experience and Publication objects to dictionaries for JSON storage
    experiences_dict = [exp.model_dump() for exp in profile_data.past_experiences]
    publications_dict = [pub.model_dump() for pub in profile_data.publications]

    # Update user profile with all fields
    current_user.university = profile_data.university
    current_user.major = profile_data.major
    current_user.graduation_year = profile_data.graduation_year
    current_user.gpa = profile_data.gpa
    current_user.resume_text = profile_data.resume_text
    current_user.past_experiences = experiences_dict
    current_user.skills = profile_data.skills
    current_user.publications = publications_dict
    current_user.research_interests = profile_data.research_interests
    current_user.preferred_methods = profile_data.preferred_methods
    current_user.preferred_datasets = profile_data.preferred_datasets
    current_user.degree_level = profile_data.experience_level or "undergraduate"
    current_user.location_preferences = profile_data.location_preferences
    current_user.availability = profile_data.availability

    db.commit()
    db.refresh(current_user)

    # Return the updated profile
    return ProfileResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        name=current_user.name,
        university=current_user.university,
        major=current_user.major,
        graduation_year=current_user.graduation_year,
        gpa=current_user.gpa,
        resume_file_path=current_user.resume_file_path,
        resume_text=current_user.resume_text,
        past_experiences=current_user.past_experiences or [],
        skills=current_user.skills or [],
        publications=current_user.publications or [],
        research_interests=current_user.research_interests,
        preferred_methods=current_user.preferred_methods or [],
        preferred_datasets=current_user.preferred_datasets or [],
        experience_level=current_user.degree_level or "undergraduate",
        location_preferences=current_user.location_preferences or [],
        availability=current_user.availability,
        created_at=current_user.created_at.isoformat(),
        updated_at=current_user.updated_at.isoformat()
    )


@router.patch("/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Partially update the student profile for the authenticated user.

    This endpoint allows updating specific fields without requiring all fields.
    Only provided fields will be updated.

    - Requires valid access token in Authorization header
    - All fields are optional

    Returns:
        ProfileResponse with updated profile data

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 422: If validation fails
    """
    # Update only provided fields
    update_data = profile_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        # Map API field name to User model column name
        if field == "experience_level":
            field = "degree_level"
        # Convert Experience and Publication lists to dictionaries if present
        if field == "past_experiences" and value is not None:
            value = [exp.model_dump() for exp in value]
        elif field == "publications" and value is not None:
            value = [pub.model_dump() for pub in value]

        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    # Return the updated profile
    return ProfileResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        name=current_user.name,
        university=current_user.university,
        major=current_user.major,
        graduation_year=current_user.graduation_year,
        gpa=current_user.gpa,
        resume_file_path=current_user.resume_file_path,
        resume_text=current_user.resume_text,
        past_experiences=current_user.past_experiences or [],
        skills=current_user.skills or [],
        publications=current_user.publications or [],
        research_interests=current_user.research_interests,
        preferred_methods=current_user.preferred_methods or [],
        preferred_datasets=current_user.preferred_datasets or [],
        experience_level=current_user.degree_level or "undergraduate",
        location_preferences=current_user.location_preferences or [],
        availability=current_user.availability,
        created_at=current_user.created_at.isoformat(),
        updated_at=current_user.updated_at.isoformat()
    )


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current user's profile.

    - Requires valid access token in Authorization header

    Returns:
        ProfileResponse with complete profile data

    Raises:
        HTTPException 401: If not authenticated
    """
    return ProfileResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        name=current_user.name,
        university=current_user.university,
        major=current_user.major,
        graduation_year=current_user.graduation_year,
        gpa=current_user.gpa,
        resume_file_path=current_user.resume_file_path,
        resume_text=current_user.resume_text,
        past_experiences=current_user.past_experiences or [],
        skills=current_user.skills or [],
        publications=current_user.publications or [],
        research_interests=current_user.research_interests,
        preferred_methods=current_user.preferred_methods or [],
        preferred_datasets=current_user.preferred_datasets or [],
        experience_level=current_user.degree_level or "undergraduate",
        location_preferences=current_user.location_preferences or [],
        availability=current_user.availability,
        created_at=current_user.created_at.isoformat(),
        updated_at=current_user.updated_at.isoformat()
    )


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user's profile by ID.

    - Requires valid access token in Authorization header
    - Can view other users' profiles (useful for admin or matching features)

    Returns:
        ProfileResponse with the requested user's profile data

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 404: If user not found
    """
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return ProfileResponse(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        university=user.university,
        major=user.major,
        graduation_year=user.graduation_year,
        gpa=user.gpa,
        resume_file_path=user.resume_file_path,
        resume_text=user.resume_text,
        past_experiences=user.past_experiences or [],
        skills=user.skills or [],
        publications=user.publications or [],
        research_interests=user.research_interests,
        preferred_methods=user.preferred_methods or [],
        preferred_datasets=user.preferred_datasets or [],
        experience_level=user.degree_level or "undergraduate",
        location_preferences=user.location_preferences or [],
        availability=user.availability,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )
