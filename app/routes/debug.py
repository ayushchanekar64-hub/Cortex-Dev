from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from app.services.debug_service import DebugService

router = APIRouter(prefix="/debug", tags=["debug"])
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class DebugRequest(BaseModel):
    files: Dict[str, str] = Field(..., description="Dictionary mapping filenames to code content")
    auto_fix: Optional[bool] = Field(True, description="Whether to automatically fix detected issues")

class ErrorInfo(BaseModel):
    type: str
    line: int
    column: int
    message: str
    severity: str

class FileAnalysis(BaseModel):
    language: str
    errors: List[ErrorInfo]
    warnings: List[ErrorInfo]
    status: str
    total_issues: int

class DebugAnalysisResponse(BaseModel):
    status: str
    total_files: int
    files_with_errors: int
    total_errors: int
    total_warnings: int
    analysis: Dict[str, FileAnalysis]
    analyzed_at: str

class FixSummary(BaseModel):
    status: str
    fixes_applied: int
    original_length: Optional[int] = None
    fixed_length: Optional[int] = None
    message: Optional[str] = None

class DebugFixResponse(BaseModel):
    status: str
    total_files: int
    files_fixed: int
    total_fixes_applied: int
    fixed_files: Dict[str, str]
    fix_summary: Dict[str, FixSummary]
    fixed_at: str

class DebugAndFixResponse(BaseModel):
    analysis: DebugAnalysisResponse
    fix_result: DebugFixResponse
    workflow_status: str
    processed_at: str

# Initialize service
debug_service = DebugService()


@router.post("/analyze", response_model=DebugAnalysisResponse)
async def analyze_code(request: DebugRequest):
    """
    Analyze generated code for errors and issues.
    """
    try:
        logger.info(f"Analyzing {len(request.files)} files for errors")
        
        if not request.files:
            raise HTTPException(status_code=400, detail="No files provided for analysis")
        
        result = await debug_service.analyze_code(request.files)
        
        if result["status"] != "completed":
            raise HTTPException(status_code=500, detail="Code analysis failed")
        
        return DebugAnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/fix", response_model=DebugFixResponse)
async def fix_code(request: DebugRequest):
    """
    Fix detected issues in generated code.
    """
    try:
        logger.info(f"Fixing issues in {len(request.files)} files")
        
        if not request.files:
            raise HTTPException(status_code=400, detail="No files provided for fixing")
        
        result = await debug_service.fix_code(request.files)
        
        if result["status"] != "completed":
            raise HTTPException(status_code=500, detail="Code fixing failed")
        
        return DebugFixResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fixing code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/debug-and-fix", response_model=DebugAndFixResponse)
async def debug_and_fix(request: DebugRequest):
    """
    Complete debug and fix workflow - analyze and fix code in one step.
    """
    try:
        logger.info(f"Starting debug and fix workflow for {len(request.files)} files")
        
        if not request.files:
            raise HTTPException(status_code=400, detail="No files provided for debugging")
        
        result = await debug_service.debug_and_fix(request.files)
        
        if result["workflow_status"] != "completed":
            raise HTTPException(status_code=500, detail="Debug and fix workflow failed")
        
        return DebugAndFixResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in debug and fix workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/sample-buggy-code")
async def get_sample_buggy_code():
    """
    Get sample buggy code for testing the debug agent.
    """
    buggy_files = {
        "main.py": '''
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Missing import for APIRouter
router = APIRouter()

# Missing colon in function definition
@app.get("/test")
async def test()
    return {"status": "test"}
''',
        
        "App.tsx": '''
import { useState } from 'react';

// Missing React import
function App() {
    const [count, setCount] = useState(0);
    
    // Mismatched braces
    return (
        <div>
            <h1>Count: {count}</h1>
            <button onClick={() => setCount(count + 1)}>
                Increment
            </button>
        </div>
    // Missing closing brace
''',
        
        "package.json": '''
{
    "name": "test-app",
    "version": "1.0.0",
    "dependencies": {
        "react": "^18.2.0",
        "fastapi": "^0.104.1",
    },
    // Trailing comma in JSON
}
'''
    }
    
    return {
        "buggy_files": buggy_files,
        "description": "Sample buggy code files for testing the Debug Agent",
        "expected_issues": [
            "Missing imports (APIRouter, React)",
            "Syntax errors (missing colon, mismatched braces)",
            "JSON formatting issues (trailing comma)"
        ]
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the debug service.
    """
    return {
        "status": "healthy",
        "service": "debug",
        "supported_languages": debug_service.get_supported_languages()
    }


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported programming languages for debugging.
    """
    return {
        "supported_languages": debug_service.get_supported_languages(),
        "language_patterns": {
            "python": [".py"],
            "javascript": [".js", ".jsx"],
            "typescript": [".ts", ".tsx"],
            "json": [".json"]
        }
    }
