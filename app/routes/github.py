from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from ..services.github_service import get_github_service

router = APIRouter(prefix="/github", tags=["github"])


class CreateRepoRequest(BaseModel):
    repo_name: str
    description: str = ""
    private: bool = False


class PushFilesRequest(BaseModel):
    owner: str
    repo: str
    files: List[Dict[str, Any]]
    project_name: str


def get_github_token(request: Request) -> Optional[str]:
    """Extract GitHub token from request headers."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("token "):
        return auth_header.replace("token ", "")
    return None


@router.get("/user")
async def get_github_user(request: Request):
    """Get authenticated GitHub user information."""
    try:
        token = get_github_token(request)
        if not token:
            raise HTTPException(status_code=401, detail="GitHub token not provided")
        
        github_service = get_github_service(token)
        user_info = await github_service.get_user_info()
        
        if not user_info.get("success"):
            raise HTTPException(status_code=401, detail=user_info.get("error", "Failed to authenticate"))
        return user_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-repo")
async def create_repository(request: CreateRepoRequest, http_request: Request):
    """Create a new GitHub repository."""
    try:
        token = get_github_token(http_request)
        if not token:
            raise HTTPException(status_code=401, detail="GitHub token not provided")
        
        github_service = get_github_service(token)
        result = await github_service.create_repository(
            repo_name=request.repo_name,
            description=request.description,
            private=request.private,
            token=token
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create repository"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push-files")
async def push_files(request: PushFilesRequest, http_request: Request):
    """Push project files to GitHub repository."""
    try:
        token = get_github_token(http_request)
        if not token:
            raise HTTPException(status_code=401, detail="GitHub token not provided")
        
        github_service = get_github_service(token)
        result = await github_service.push_project_files(
            owner=request.owner,
            repo=request.repo,
            files=request.files,
            project_name=request.project_name,
            token=token
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to push files"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
