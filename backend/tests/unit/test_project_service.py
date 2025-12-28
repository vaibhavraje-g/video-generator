# backend/tests/unit/test_project_service.py
"""Unit tests for project service"""

import pytest
from app.models import ProjectCreate
from app.services.project_service import ProjectService


@pytest.mark.asyncio
async def test_create_project(test_db, test_user, valid_project_data):
    """Test successful project creation"""
    user, _ = test_user
    project_service = ProjectService()
    
    project_data = ProjectCreate(**valid_project_data)
    project = await project_service.create_project(str(user.id), project_data)
    
    assert project.name == valid_project_data["name"]
    assert project.description == valid_project_data["description"]
    assert str(project.user_id) == str(user.id)


@pytest.mark.asyncio
async def test_get_user_projects(test_db, test_user, valid_project_data):
    """Test retrieving user's projects"""
    user, _ = test_user
    project_service = ProjectService()
    
    # Create multiple projects
    for i in range(3):
        project_data = ProjectCreate(
            name=f"Project {i}",
            description=f"Description {i}"
        )
        await project_service.create_project(str(user.id), project_data)
    
    # Retrieve projects
    projects = await project_service.get_user_projects(str(user.id))
    
    assert len(projects) == 3


@pytest.mark.asyncio
async def test_get_user_projects_pagination(test_db, test_user):
    """Test project pagination"""
    user, _ = test_user
    project_service = ProjectService()
    
    # Create 5 projects
    for i in range(5):
        project_data = ProjectCreate(
            name=f"Project {i}",
            description=f"Description {i}"
        )
        await project_service.create_project(str(user.id), project_data)
    
    # Test pagination
    first_page = await project_service.get_user_projects(str(user.id), skip=0, limit=2)
    second_page = await project_service.get_user_projects(str(user.id), skip=2, limit=2)
    
    assert len(first_page) == 2
    assert len(second_page) == 2
    assert first_page[0].id != second_page[0].id  # Different projects


@pytest.mark.asyncio
async def test_get_project_with_ownership(test_db, test_user, valid_project_data):
    """Test retrieving project with ownership verification"""
    user, _ = test_user
    project_service = ProjectService()
    
    # Create project
    project_data = ProjectCreate(**valid_project_data)
    project = await project_service.create_project(str(user.id), project_data)
    
    # Retrieve project
    retrieved_project = await project_service.get_project(str(project.id), str(user.id))
    
    assert retrieved_project is not None
    assert retrieved_project.id == project.id


@pytest.mark.asyncio
async def test_get_project_unauthorized(test_db, auth_service, valid_user_data, valid_project_data):
    """Test that users cannot access other users' projects"""
    project_service = ProjectService()
    
    # Create first user and their project
    user1_data = UserCreate(**valid_user_data)
    user1 = await auth_service.create_user(user1_data)
    
    project_data = ProjectCreate(**valid_project_data)
    project = await project_service.create_project(str(user1.id), project_data)
    
    # Create second user
    user2_data = UserCreate(
        email="different@example.com",
        username="differentuser",
        password="password123"
    )
    user2 = await auth_service.create_user(user2_data)
    
    # Try to access user1's project as user2
    retrieved_project = await project_service.get_project(str(project.id), str(user2.id))
    
    assert retrieved_project is None  # Should not be able to access


@pytest.mark.asyncio
async def test_delete_project(test_db, test_user, valid_project_data):
    """Test project deletion"""
    user, _ = test_user
    project_service = ProjectService()
    
    # Create project
    project_data = ProjectCreate(**valid_project_data)
    project = await project_service.create_project(str(user.id), project_data)
    
    # Delete project
    deleted = await project_service.delete_project(str(project.id), str(user.id))
    
    assert deleted is True
    
    # Verify project is deleted
    retrieved_project = await project_service.get_project(str(project.id), str(user.id))
    assert retrieved_project is None
