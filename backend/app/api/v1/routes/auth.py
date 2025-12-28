# backend/app/api/v1/routes/auth.py
"""Authentication routes"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from app.services.auth_service import AuthService
from app.models import UserCreate, UserResponse, User
from app.middleware import get_current_active_user

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request model"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    
    Returns:
        Created user information
    """
    auth_service = AuthService()
    
    try:
        user = await auth_service.create_user(user_data)
        
        # Convert to response model
        return UserResponse(
            _id=str(user.id),
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """
    Login with email and password
    
    Returns:
        JWT access and refresh tokens
    """
    auth_service = AuthService()
    
    user = await auth_service.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = auth_service.create_tokens(user)
    return TokenResponse(**tokens)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    
    Returns:
        Current user data
    """
    return UserResponse(
        _id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
