from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from app.services.generator_service import GeneratorService

router = APIRouter(prefix="/generator", tags=["generator"])
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class GeneratorRequest(BaseModel):
    plan: Dict[str, Any] = Field(..., description="Planner JSON output")
    components: Optional[List[str]] = Field(
        default=["frontend", "backend"],
        description="Components to generate: ['frontend', 'backend']"
    )

class GeneratedFile(BaseModel):
    filename: str
    content: str

class ComponentFiles(BaseModel):
    component: str
    files: Dict[str, str] = Field(..., description="Filename to content mapping")

class GeneratorResponse(BaseModel):
    status: str
    project_name: str
    generated_at: str
    files: Dict[str, Dict[str, str]] = Field(..., description="Component to files mapping")
    total_files: int

class SampleOutputResponse(BaseModel):
    sample_files: Dict[str, str]
    description: str

# Initialize service
generator_service = GeneratorService()


@router.post("/generate", response_model=GeneratorResponse)
async def generate_code(request: GeneratorRequest):
    """
    Generate full code files from planner JSON.
    """
    try:
        logger.info(f"Generating code for project: {request.plan.get('project_name', 'Unknown')}")
        
        # Validate components
        supported_components = generator_service.get_supported_components()
        invalid_components = [c for c in request.components if c not in supported_components]
        
        if invalid_components:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported components: {invalid_components}. Supported: {supported_components}"
            )
        
        result = await generator_service.generate_code(
            plan=request.plan,
            components=request.components
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return GeneratorResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/sample-output", response_model=SampleOutputResponse)
async def get_sample_output():
    """
    Get sample output of generated code files.
    """
    sample_files = {
        "frontend/package.json": '''{
  "name": "task-manager-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0",
    "tailwindcss": "^3.2.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  }
}''',
        
        "frontend/src/App.tsx": '''import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;''',
        
        "backend/main.py": '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, tasks

app = FastAPI(
    title="Task Management API",
    description="FastAPI backend for task management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Task Management API"}''',
        
        "backend/requirements.txt": '''fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
pydantic==2.5.0
sqlalchemy==2.0.0
psycopg2-binary==2.9.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4'''
    }
    
    return {
        "sample_files": sample_files,
        "description": "Sample output from the Code Generator Agent showing generated React frontend and FastAPI backend files"
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the generator service.
    """
    return {
        "status": "healthy",
        "service": "generator",
        "supported_components": generator_service.get_supported_components()
    }


@router.get("/components")
async def get_supported_components():
    """
    Get list of supported components for code generation.
    """
    return {
        "supported_components": generator_service.get_supported_components(),
        "description": "List of components that can be generated by the Code Generator Agent"
    }
