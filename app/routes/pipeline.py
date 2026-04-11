from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from app.services.pipeline_service import PipelineService
from app.services.ai_service import AIService

router = APIRouter(prefix="/pipeline", tags=["pipeline"])
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class PipelineRequest(BaseModel):
    prompt: str = Field(..., description="User's project description or prompt")
    components: Optional[List[str]] = Field(
        default=["frontend", "backend"],
        description="Components to generate: ['frontend', 'backend']"
    )
    auto_fix: Optional[bool] = Field(default=True, description="Whether to automatically fix detected issues")
    generate_tests: Optional[bool] = Field(default=True, description="Whether to generate test cases")
    validate_api: Optional[bool] = Field(default=False, description="Whether to validate API endpoints")
    model: Optional[str] = Field(default="gpt-3.5-turbo", description="OpenAI model for planning")
    max_tokens: Optional[int] = Field(default=2000, description="Maximum tokens for planning")

class PipelineStepRequest(BaseModel):
    step: str = Field(..., description="Pipeline step to run: 'planning', 'generation', 'debugging', 'testing'")
    input_data: Dict[str, Any] = Field(..., description="Input data for the step")
    options: Optional[Dict[str, Any]] = Field(default={}, description="Additional options for the step")

class StageResult(BaseModel):
    status: str
    duration_seconds: float
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class PipelineStages(BaseModel):
    planning: Optional[StageResult] = None
    generation: Optional[StageResult] = None
    debugging: Optional[StageResult] = None
    testing: Optional[StageResult] = None

class PipelineSummary(BaseModel):
    total_stages: int
    completed_stages: int
    failed_stages: int
    total_errors: int
    total_warnings: int
    features_planned: Optional[int] = None
    files_generated: Optional[int] = None
    errors_found: Optional[int] = None
    fixes_applied: Optional[int] = None
    tests_run: Optional[int] = None
    test_success_rate: Optional[float] = None

class FinalOutput(BaseModel):
    project_plan: Dict[str, Any]
    generated_code: Dict[str, Any]
    debug_results: Dict[str, Any]
    test_results: Dict[str, Any]
    summary: PipelineSummary

class PipelineResponse(BaseModel):
    user_prompt: str
    pipeline_status: str
    stages: PipelineStages
    final_output: Optional[FinalOutput] = None
    errors: List[str] = []
    warnings: List[str] = []
    started_at: str
    completed_at: Optional[str] = None
    total_duration_seconds: Optional[float] = None

class PipelineStatusResponse(BaseModel):
    services: Dict[str, Dict[str, Any]]
    pipeline_status: str

class ModifyRequest(BaseModel):
    files: List[Dict[str, str]]
    request: str
    model: Optional[str] = "gemini-2.0-flash"

class ModifyResponse(BaseModel):
    modified_files: List[Dict[str, str]]
    message: str

# Initialize service
pipeline_service = PipelineService()
ai_service = AIService()


@router.post("/generate", response_model=PipelineResponse)
async def run_full_pipeline(request: PipelineRequest):
    """
    Run the complete pipeline: User Prompt → Planner → Generator → Debug → Tester → Final Output.
    """
    try:
        logger.info(f"Starting full pipeline for: {request.prompt[:100]}...")
        
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Validate components
        supported_components = ["frontend", "backend"]
        invalid_components = [c for c in request.components if c not in supported_components]
        if invalid_components:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported components: {invalid_components}. Supported: {supported_components}"
            )
        
        # Run the full pipeline
        result = await pipeline_service.run_full_pipeline(
            user_prompt=request.prompt,
            components=request.components,
            auto_fix=request.auto_fix,
            generate_tests=request.generate_tests,
            validate_api=request.validate_api
        )
        
        # Convert stages to proper format
        stages = PipelineStages()
        for stage_name, stage_data in result.get("stages", {}).items():
            stage_result = StageResult(
                status=stage_data.get("status", "unknown"),
                duration_seconds=stage_data.get("duration_seconds", 0.0),
                result=stage_data.get("result"),
                error=stage_data.get("error")
            )
            setattr(stages, stage_name, stage_result)
        
        # Prepare final output
        final_output = None
        if result.get("pipeline_status") == "completed" and "final_output" in result:
            final_output = FinalOutput(
                project_plan=result["final_output"].get("project_plan", {}),
                generated_code=result["final_output"].get("generated_code", {}),
                debug_results=result["final_output"].get("debug_results", {}),
                test_results=result["final_output"].get("test_results", {}),
                summary=PipelineSummary(**result["final_output"].get("summary", {}))
            )
        
        return PipelineResponse(
            user_prompt=result["user_prompt"],
            pipeline_status=result["pipeline_status"],
            stages=stages,
            final_output=final_output,
            errors=result.get("errors", []),
            warnings=result.get("warnings", []),
            started_at=result["started_at"],
            completed_at=result.get("completed_at"),
            total_duration_seconds=result.get("total_duration_seconds")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running full pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/step", response_model=Dict[str, Any])
async def run_pipeline_step(request: PipelineStepRequest):
    """
    Run a specific step in the pipeline.
    """
    try:
        logger.info(f"Running pipeline step: {request.step}")
        
        valid_steps = ["planning", "generation", "debugging", "testing"]
        if request.step not in valid_steps:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid step. Valid steps: {valid_steps}"
            )
        
        result = await pipeline_service.run_pipeline_step(
            step=request.step,
            input_data=request.input_data,
            options=request.options
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running pipeline step: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/progress")
async def get_pipeline_progress():
    """
    Get the real-time progress of the running pipeline.
    """
    return pipeline_service.get_progress()

@router.get("/status", response_model=PipelineStatusResponse)
async def get_pipeline_status():
    """
    Get the status of all pipeline services.
    """
    try:
        status = pipeline_service.get_pipeline_status()
        
        return PipelineStatusResponse(
            services=status,
            pipeline_status="ready"
        )
        
    except Exception as e:
        logger.error(f"Error getting pipeline status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/example")
async def get_pipeline_example():
    """
    Get an example of a complete pipeline request and response.
    """
    example_request = {
        "prompt": "Build a task management web app with user authentication and real-time updates",
        "components": ["frontend", "backend"],
        "auto_fix": True,
        "generate_tests": True,
        "validate_api": False
    }
    
    example_response = {
        "user_prompt": "Build a task management web app with user authentication and real-time updates",
        "pipeline_status": "completed",
        "stages": {
            "planning": {
                "status": "completed",
                "duration_seconds": 3.2,
                "result": {
                    "plan": {
                        "project_name": "Task Management App",
                        "features": [
                            {"name": "User Authentication", "priority": "high"},
                            {"name": "Task Management", "priority": "high"}
                        ]
                    }
                }
            },
            "generation": {
                "status": "completed",
                "duration_seconds": 5.1,
                "result": {
                    "total_files": 12,
                    "files": {
                        "frontend": {
                            "src/App.tsx": "// React app code",
                            "package.json": "// Dependencies"
                        },
                        "backend": {
                            "main.py": "# FastAPI code",
                            "requirements.txt": "# Python dependencies"
                        }
                    }
                }
            },
            "debugging": {
                "status": "completed",
                "duration_seconds": 2.8,
                "result": {
                    "analysis": {"total_errors": 0, "total_warnings": 2},
                    "fix_result": {"total_fixes_applied": 2}
                }
            },
            "testing": {
                "status": "completed",
                "duration_seconds": 4.5,
                "result": {
                    "test_generation": {"total_tests_generated": 8},
                    "test_execution": {"total_tests_run": 8, "success_rate": 100.0}
                }
            }
        },
        "final_output": {
            "project_plan": {"project_name": "Task Management App"},
            "generated_code": {"frontend": {}, "backend": {}},
            "debug_results": {},
            "test_results": {},
            "summary": {
                "total_stages": 4,
                "completed_stages": 4,
                "failed_stages": 0,
                "total_errors": 0,
                "files_generated": 12,
                "tests_run": 8,
                "test_success_rate": 100.0
            }
        },
        "errors": [],
        "warnings": [],
        "total_duration_seconds": 15.6
    }
    
    return {
        "example_request": example_request,
        "example_response": example_response,
        "description": "Example of a complete pipeline execution from user prompt to final output"
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the pipeline service.
    """
    try:
        status = pipeline_service.get_pipeline_status()
        
        return {
            "status": "healthy",
            "service": "pipeline",
            "services_status": status,
            "pipeline_ready": all(
                service.get("configured", False) 
                for service in status.values()
            )
        }
        
    except Exception as e:
        logger.error(f"Error in pipeline health check: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "pipeline",
            "error": str(e)
        }


@router.get("/workflow")
async def get_workflow_info():
    """
    Get information about the pipeline workflow and stages.
    """
    return {
        "workflow": "User Prompt → Planner → Generator → Debug → Tester → Final Output",
        "stages": [
            {
                "name": "planning",
                "description": "Convert user prompt into structured project plan",
                "input": "User prompt text",
                "output": "JSON project plan with tech stack, features, and file structure",
                "service": "PlannerService"
            },
            {
                "name": "generation",
                "description": "Generate full code files based on project plan",
                "input": "Project plan JSON",
                "output": "Generated code files (frontend/backend)",
                "service": "GeneratorService"
            },
            {
                "name": "debugging",
                "description": "Analyze and fix errors in generated code",
                "input": "Generated code files",
                "output": "Fixed code files and debug report",
                "service": "DebugService"
            },
            {
                "name": "testing",
                "description": "Generate and run test cases for the code",
                "input": "Fixed code files",
                "output": "Test files and test results",
                "service": "TesterService"
            }
        ],
        "total_stages": 4,
        "parallel_execution": False,
        "error_handling": "Continues on non-critical errors"
    }


@router.post("/modify", response_model=ModifyResponse)
async def modify_code(request: ModifyRequest):
    """
    Modify generated code based on user's request using AI.
    """
    try:
        logger.info(f"Modifying code based on request: {request.request[:100]}...")
        
        if not request.files:
            raise HTTPException(status_code=400, detail="No files provided for modification")
        
        if not request.request.strip():
            raise HTTPException(status_code=400, detail="Modification request cannot be empty")
        
        # Create prompt for AI to modify code
        files_context = "\n\n".join([
            f"File: {f.get('path', f.get('name', 'unknown'))}\n{f.get('content', '')}"
            for f in request.files
        ])
        
        modify_prompt = f"""You are a code modification expert. Here is the current project code:

{files_context}

User's modification request: {request.request}

Please modify the code according to the user's request. Return the modified files in JSON format with this structure:
{{
  "modified_files": [
    {{
      "path": "file path",
      "content": "modified content"
    }}
  ],
  "message": "brief description of changes made"
}}

IMPORTANT:
- Only modify files that need to change
- Keep the same file structure
- Make minimal, focused changes
- Ensure code remains valid and functional
- Return ONLY valid JSON, no markdown
"""

        # Call AI service
        response = await ai_service._generate_gemini_json(
            prompt=modify_prompt,
            system_instruction="You are a code modification expert. Modify code based on user requests and return the result in valid JSON format."
        )
        
        if not response or "modified_files" not in response:
            raise HTTPException(status_code=500, detail="Invalid response from AI service")
        
        return ModifyResponse(
            modified_files=response.get("modified_files", []),
            message=response.get("message", "Code modified successfully")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error modifying code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
