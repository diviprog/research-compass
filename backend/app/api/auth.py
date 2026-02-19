"""
Authentication API endpoints for user registration, login, token refresh, and logout.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import (
    UserSignUp,
    UserSignIn,
    TokenRefresh,
    AuthResponse,
    TokenPair,
    UserResponse
)
from app.core.auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignUp, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    - Validates email format, password strength, and required fields
    - Hashes password with bcrypt (salt rounds 12)
    - Creates user account and returns JWT tokens
    
    Returns:
        AuthResponse with user data and JWT tokens
        
    Raises:
        HTTPException 400: If email already registered
        HTTPException 422: If validation fails
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
        research_interests="",  # Can be updated later
        preferred_methods=None,
        preferred_datasets=None
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate JWT tokens
    access_token = create_access_token(data={"sub": new_user.user_id})
    refresh_token_str = create_refresh_token(data={"sub": new_user.user_id})
    
    # Store refresh token in database
    refresh_token = RefreshToken(
        token=refresh_token_str,
        user_id=new_user.user_id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token)
    db.commit()
    
    # Prepare response
    user_response = UserResponse(
        user_id=new_user.user_id,
        email=new_user.email,
        name=new_user.name,
        created_at=new_user.created_at.isoformat()
    )
    
    return AuthResponse(
        user=user_response,
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(credentials: UserSignIn, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT tokens.
    
    - Validates email and password
    - Returns access token (15min expiry) and refresh token (7day expiry)
    
    Returns:
        AuthResponse with user data and JWT tokens
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Authenticate user
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT tokens
    access_token = create_access_token(data={"sub": user.user_id})
    refresh_token_str = create_refresh_token(data={"sub": user.user_id})
    
    # Store refresh token in database
    refresh_token = RefreshToken(
        token=refresh_token_str,
        user_id=user.user_id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token)
    db.commit()
    
    # Prepare response
    user_response = UserResponse(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        created_at=user.created_at.isoformat()
    )
    
    return AuthResponse(
        user=user_response,
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Refresh access token using a valid refresh token.
    
    - Validates refresh token
    - Returns new access token and refresh token
    - Revokes old refresh token
    
    Returns:
        TokenPair with new access and refresh tokens
        
    Raises:
        HTTPException 401: If refresh token is invalid, expired, or revoked
    """
    # Decode and validate refresh token
    try:
        payload = decode_token(token_data.refresh_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user_id from payload
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if refresh token exists and is valid in database
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token
    ).first()
    
    if not db_token or not db_token.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Revoke old refresh token
    db_token.is_revoked = True
    
    # Generate new tokens
    new_access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    # Store new refresh token
    new_token_record = RefreshToken(
        token=new_refresh_token,
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_token_record)
    db.commit()
    
    return TokenPair(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token_data: TokenRefresh,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking their refresh token.
    
    - Requires valid access token in Authorization header
    - Revokes the provided refresh token
    
    Returns:
        Success message
        
    Raises:
        HTTPException 401: If not authenticated
        HTTPException 404: If refresh token not found
    """
    # Find and revoke the refresh token
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token,
        RefreshToken.user_id == current_user.user_id
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found"
        )
    
    # Revoke the token
    db_token.is_revoked = True
    db.commit()
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    - Requires valid access token in Authorization header
    
    Returns:
        UserResponse with current user data
        
    Raises:
        HTTPException 401: If not authenticated
    """
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at.isoformat()
    )

