# backend/tests/unit/test_auth_service.py
"""Unit tests for authentication service"""

import pytest
from app.models import UserCreate
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_create_user_success(auth_service, valid_user_data):
    """Test successful user creation"""
    user_data = UserCreate(**valid_user_data)
    user = await auth_service.create_user(user_data)
    
    assert user.email == valid_user_data["email"]
    assert user.username == valid_user_data["username"]
    assert user.is_active is True
    assert user.hashed_password != valid_user_data["password"]  # Password should be hashed


@pytest.mark.asyncio
async def test_create_user_duplicate_email(auth_service, test_user, valid_user_data):
    """Test user creation with duplicate email fails"""
    user, _ = test_user
    
    # Try to create user with same email
    duplicate_data = UserCreate(
        email=user.email,  # Same email
        username="different_username",
        password="password123"
    )
    
    with pytest.raises(ValueError, match="Email already registered"):
        await auth_service.create_user(duplicate_data)


@pytest.mark.asyncio
async def test_create_user_duplicate_username(auth_service, test_user, valid_user_data):
    """Test user creation with duplicate username fails"""
    user, _ = test_user
    
    # Try to create user with same username
    duplicate_data = UserCreate(
        email="different@example.com",
        username=user.username,  # Same username
        password="password123"
    )
    
    with pytest.raises(ValueError, match="Username already taken"):
        await auth_service.create_user(duplicate_data)


@pytest.mark.asyncio
async def test_authenticate_user_success(auth_service, test_user):
    """Test successful user authentication"""
    user, password = test_user
    
    authenticated_user = await auth_service.authenticate_user(user.email, password)
    
    assert authenticated_user is not None
    assert authenticated_user.email == user.email


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(auth_service, test_user):
    """Test authentication with wrong password fails"""
    user, _ = test_user
    
    authenticated_user = await auth_service.authenticate_user(user.email, "wrongpassword")
    
    assert authenticated_user is None


@pytest.mark.asyncio
async def test_authenticate_user_nonexistent(auth_service):
    """Test authentication with non-existent email fails"""
    authenticated_user = await auth_service.authenticate_user(
        "nonexistent@example.com",
        "password123"
    )
    
    assert authenticated_user is None


@pytest.mark.asyncio
async def test_get_user_by_id(auth_service, test_user):
    """Test retrieving user by ID"""
    user, _ = test_user
    
    retrieved_user = await auth_service.get_user_by_id(str(user.id))
    
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.email == user.email


@pytest.mark.asyncio
async def test_get_user_by_email(auth_service, test_user):
    """Test retrieving user by email"""
    user, _ = test_user
    
    retrieved_user = await auth_service.get_user_by_email(user.email)
    
    assert retrieved_user is not None
    assert retrieved_user.email == user.email


@pytest.mark.asyncio
async def test_create_tokens(auth_service, test_user):
    """Test JWT token creation"""
    user, _ = test_user
    
    tokens = auth_service.create_tokens(user)
    
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert "token_type" in tokens
    assert tokens["token_type"] == "bearer"
    assert len(tokens["access_token"]) > 0
    assert len(tokens["refresh_token"]) > 0
