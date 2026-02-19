"""
Pydantic schemas for authentication and user management.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class UserSignUp(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User's password (min 8 characters)")
    name: str = Field(..., min_length=2, max_length=255, description="User's full name")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "email": "researcher@university.edu",
                "password": "SecurePass123",
                "name": "Dr. Jane Smith"
            }]
        }
    }


class UserSignIn(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "email": "researcher@university.edu",
                "password": "SecurePass123"
            }]
        }
    }


class Token(BaseModel):
    """Schema for access token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }]
        }
    }


class TokenPair(BaseModel):
    """Schema for access and refresh token pair."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }]
        }
    }


class TokenRefresh(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str = Field(..., description="Refresh token")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }]
        }
    }


class UserResponse(BaseModel):
    """Schema for user data in API responses."""
    user_id: int = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    created_at: str = Field(..., description="Account creation timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [{
                "user_id": 1,
                "email": "researcher@university.edu",
                "name": "Dr. Jane Smith",
                "created_at": "2025-10-25T12:00:00"
            }]
        }
    }


class AuthResponse(BaseModel):
    """Schema for successful authentication response with user data and tokens."""
    user: UserResponse = Field(..., description="Authenticated user data")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "user": {
                    "user_id": 1,
                    "email": "researcher@university.edu",
                    "name": "Dr. Jane Smith",
                    "created_at": "2025-10-25T12:00:00"
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }]
        }
    }

