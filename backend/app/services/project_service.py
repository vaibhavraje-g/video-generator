# backend/app/services/project_service.py
"""Project management service"""

from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.db import get_database
from app.models import ProjectCreate, Project


class ProjectService:
    """Service for project management"""
    
    def __init__(self):
        self.db = get_database()
        self.projects_collection = self.db.projects
        self.videos_collection = self.db.videos
    
    async def create_project(self, user_id: str, project_data: ProjectCreate) -> Project:
        """Create a new project for a user"""
        project_dict = {
            "user_id": ObjectId(user_id),
            "name": project_data.name,
            "description": project_data.description,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = await self.projects_collection.insert_one(project_dict)
        project_dict["_id"] = result.inserted_id
        
        return Project(**project_dict)
    
    async def get_user_projects(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> List[Project]:
        """Get all projects for a user with pagination"""
        cursor = self.projects_collection.find(
            {"user_id": ObjectId(user_id)}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        projects = []
        async for project_dict in cursor:
            projects.append(Project(**project_dict))
        
        return projects
    
    async def get_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """Get a specific project with ownership verification"""
        if not ObjectId.is_valid(project_id):
            return None
        
        project_dict = await self.projects_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": ObjectId(user_id)
        })
        
        if not project_dict:
            return None
        
        return Project(**project_dict)
    
    async def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete a project and all associated videos"""
        if not ObjectId.is_valid(project_id):
            return False
        
        project = await self.get_project(project_id, user_id)
        if not project:
            return False
        
        # Delete associated videos
        await self.videos_collection.delete_many({"project_id": ObjectId(project_id)})
        
        # Delete project
        result = await self.projects_collection.delete_one({
            "_id": ObjectId(project_id),
            "user_id": ObjectId(user_id)
        })
        
        return result.deleted_count > 0
    
    async def get_project_history(self, project_id: str, user_id: str) -> List[dict]:
        """Get video generation history for a project"""
        project = await self.get_project(project_id, user_id)
        if not project:
            return []
        
        cursor = self.videos_collection.find(
            {"project_id": ObjectId(project_id)}
        ).sort("created_at", -1)
        
        videos = []
        async for video_dict in cursor:
            videos.append(video_dict)
        
        return videos
