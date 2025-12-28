# backend/app/api/v1/routes/projects.py
"""Project management routes"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.services.project_service import ProjectService
from app.models import ProjectCreate, ProjectResponse, User
from app.middleware import get_current_active_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new project
    
    Returns:
        Created project
    """
    project_service = ProjectService()
    project = await project_service.create_project(str(current_user.id), project_data)
    
    return ProjectResponse(
        _id=str(project.id),
        user_id=str(project.user_id),
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """
    List user's projects with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of projects
    """
    project_service = ProjectService()
    projects = await project_service.get_user_projects(
        str(current_user.id), skip, limit
    )
    
    return [
        ProjectResponse(
            _id=str(p.id),
            user_id=str(p.user_id),
            name=p.name,
            description=p.description,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific project
    
    Returns:
        Project details
    """
    project_service = ProjectService()
    project = await project_service.get_project(project_id, str(current_user.id))
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return ProjectResponse(
        _id=str(project.id),
        user_id=str(project.user_id),
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a project and all associated videos
    """
    project_service = ProjectService()
    deleted = await project_service.delete_project(project_id, str(current_user.id))
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


@router.get("/{project_id}/history")
async def get_project_history(
    project_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get video generation history for a project
    
    Returns:
        List of videos in the project
    """
    project_service = ProjectService()
    videos = await project_service.get_project_history(project_id, str(current_user.id))
    
    return {"videos": videos}
