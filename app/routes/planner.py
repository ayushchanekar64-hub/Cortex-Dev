from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging

from app.services.planner_service import PlannerService

router = APIRouter(prefix="/planner", tags=["planner"])
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class PlannerRequest(BaseModel):
    prompt: str = Field(..., description="User prompt describing the project to plan")
    model: Optional[str] = Field("gpt-3.5-turbo", description="OpenAI model to use")
    max_tokens: Optional[int] = Field(2000, description="Maximum tokens in response")
    temperature: Optional[float] = Field(0.3, description="Response randomness (0.0-1.0)")
    plan_type: Optional[str] = Field("detailed", description="Type of plan: 'detailed' or 'simple'")

class TechStack(BaseModel):
    frontend: List[str] = []
    backend: List[str] = []
    database: List[str] = []
    tools: List[str] = []
    deployment: List[str] = []

class Feature(BaseModel):
    name: str
    description: str
    priority: str = Field(..., pattern="^(high|medium|low)$")
    estimated_hours: str

class Directory(BaseModel):
    name: str
    description: str
    files: List[str] = []

class FileStructure(BaseModel):
    root: str
    directories: List[Directory] = []

class ProjectPlan(BaseModel):
    project_name: str
    description: str
    tech_stack: TechStack
    features: List[Feature]
    file_structure: FileStructure
    implementation_steps: List[str]

class PlannerResponse(BaseModel):
    plan: ProjectPlan
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    status: str
    type: Optional[str] = None

class SimplePlannerResponse(BaseModel):
    plan: Dict[str, Any]
    status: str
    type: str

# Initialize service
planner_service = PlannerService()


@router.post("/plan", response_model=PlannerResponse)
async def create_project_plan(request: PlannerRequest):
    """
    Create a detailed project plan from user prompt using OpenAI.
    """
    try:
        logger.info(f"Creating detailed project plan for: {request.prompt[:100]}...")
        
        if not planner_service.is_configured():
            raise HTTPException(
                status_code=503, 
                detail="Planner service not configured. Please set OPENAI_API_KEY in your environment."
            )
        
        result = await planner_service.create_project_plan(
            user_prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return PlannerResponse(**result)
        
    except ValueError as e:
        logger.error(f"Validation error in planning: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating project plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/plan/simple", response_model=SimplePlannerResponse)
async def create_simple_plan(
    prompt: str,
    focus_area: str = "general"
):
    """
    Create a simple project plan for quick prototyping.
    """
    try:
        logger.info(f"Creating simple project plan for: {prompt[:100]}...")
        
        result = await planner_service.create_simple_plan(
            user_prompt=prompt,
            focus_area=focus_area
        )
        
        return SimplePlannerResponse(**result)
        
    except Exception as e:
        logger.error(f"Error creating simple plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the planner service.
    """
    return {
        "status": "healthy",
        "service": "planner",
        "openai_configured": planner_service.is_configured()
    }


@router.get("/example")
async def get_example_plan():
    """
    Get an example of a structured project plan.
    """
    example_plan = {
        "project_name": "Task Management API",
        "description": "A RESTful API for managing tasks and projects with user authentication",
        "tech_stack": {
            "frontend": ["React", "TypeScript", "TailwindCSS"],
            "backend": ["FastAPI", "Python", "Pydantic"],
            "database": ["PostgreSQL", "SQLAlchemy"],
            "tools": ["Docker", "Git", "pytest", "Black"],
            "deployment": ["AWS", "Docker Hub", "GitHub Actions"]
        },
        "features": [
            {
                "name": "User Authentication",
                "description": "JWT-based authentication with registration and login",
                "priority": "high",
                "estimated_hours": "12-16"
            },
            {
                "name": "Task Management",
                "description": "CRUD operations for tasks with status tracking",
                "priority": "high",
                "estimated_hours": "8-12"
            },
            {
                "name": "Project Organization",
                "description": "Group tasks into projects with team management",
                "priority": "medium",
                "estimated_hours": "16-20"
            },
            {
                "name": "API Documentation",
                "description": "OpenAPI/Swagger documentation with interactive testing",
                "priority": "medium",
                "estimated_hours": "4-6"
            },
            {
                "name": "Real-time Updates",
                "description": "WebSocket integration for live task updates",
                "priority": "low",
                "estimated_hours": "12-16"
            }
        ],
        "file_structure": {
            "root": "task-management-api",
            "directories": [
                {
                    "name": "app",
                    "description": "Main application code",
                    "files": ["main.py", "config.py", "database.py"]
                },
                {
                    "name": "app/models",
                    "description": "Database models and schemas",
                    "files": ["user.py", "task.py", "project.py"]
                },
                {
                    "name": "app/routes",
                    "description": "API route handlers",
                    "files": ["auth.py", "tasks.py", "projects.py"]
                },
                {
                    "name": "app/services",
                    "description": "Business logic services",
                    "files": ["auth_service.py", "task_service.py"]
                },
                {
                    "name": "tests",
                    "description": "Unit and integration tests",
                    "files": ["test_auth.py", "test_tasks.py"]
                }
            ]
        },
        "implementation_steps": [
            "Setup project structure and virtual environment",
            "Configure database connection and models",
            "Implement user authentication system",
            "Create task management endpoints",
            "Add project organization features",
            "Implement API documentation",
            "Add comprehensive testing",
            "Setup deployment pipeline"
        ]
    }
    
    return {
        "example_plan": example_plan,
        "description": "Example of a structured project plan output"
    }
