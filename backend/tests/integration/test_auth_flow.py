# backend/tests/integration/test_auth_flow.py
"""Integration tests for authentication flow"""

import pytest
from httpx import AsyncClient

from app.main import app
from app.models import UserCreate
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_login_flow(test_db, valid_user_data):
    """Test complete registration and login flow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register
        register_response = await client.post(
            "/api/v1/auth/register",
            json=valid_user_data
        )
        
        assert register_response.status_code == 201
        user_data = register_response.json()
        assert user_data["email"] == valid_user_data["email"]
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": valid_user_data["email"],
                "password": valid_user_data["password"]
            }
        )
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data


@pytest.mark.asyncio
async def test_protected_route_access(test_db, test_user_tokens):
    """Test accessing protected route with valid token"""
    user, tokens = test_user_tokens
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == user.email


@pytest.mark.asyncio
async def test_protected_route_without_token(test_db):
    """Test accessing protected route without token fails"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_protected_route_invalid_token(test_db):
    """Test accessing protected route with invalid token fails"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401  # Unauthorized
