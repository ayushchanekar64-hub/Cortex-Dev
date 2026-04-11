from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from app.services.generate_service import GenerateService
from app.services.openai_service import OpenAIService

router = APIRouter(prefix="/generate", tags=["generate"])
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gpt-3.5-turbo"
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    use_openai: Optional[bool] = True

class GenerateResponse(BaseModel):
    content: str
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None
    status: str
    tokens_used: Optional[int] = None

class CodeGenerateRequest(BaseModel):
    language: str
    description: str
    model: Optional[str] = "gpt-3.5-turbo"
    max_tokens: Optional[int] = 1500
    use_openai: Optional[bool] = True

class CodeGenerateResponse(BaseModel):
    code: str
    language: str
    description: str
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None
    status: str

# Initialize services
generate_service = GenerateService()
openai_service = OpenAIService()


@router.post("/", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    """
    Generate content based on the provided prompt using OpenAI API.
    """
    try:
        logger.info(f"Generating content for prompt: {request.prompt[:100]}...")
        
        if request.use_openai:
            if not openai_service.is_configured():
                raise HTTPException(
                    status_code=503, 
                    detail="OpenAI service not configured. Please set OPENAI_API_KEY in your environment."
                )
            
            result = await openai_service.generate_response(
                prompt=request.prompt,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            return GenerateResponse(
                content=result["content"],
                model=result["model"],
                usage=result["usage"],
                status=result["status"],
                tokens_used=result["usage"]["total_tokens"]
            )
        else:
            # Fallback to mock service
            mock_result = await generate_service.generate_content(
                prompt=request.prompt,
                options={"model": request.model, "temperature": request.temperature}
            )
            
            return GenerateResponse(**mock_result)
        
    except ValueError as e:
        logger.error(f"Validation error in content generation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/code", response_model=CodeGenerateResponse)
async def generate_code(request: CodeGenerateRequest):
    """
    Generate code based on language and description using OpenAI API.
    """
    try:
        logger.info(f"Generating {request.language} code for: {request.description[:100]}...")
        
        if request.use_openai:
            if not openai_service.is_configured():
                raise HTTPException(
                    status_code=503, 
                    detail="OpenAI service not configured. Please set OPENAI_API_KEY in your environment."
                )
            
            result = await openai_service.generate_code(
                description=request.description,
                language=request.language,
                model=request.model,
                max_tokens=request.max_tokens
            )
            
            return CodeGenerateResponse(
                code=result["code"],
                language=result["language"],
                description=result["description"],
                model=result["model"],
                usage=result["usage"],
                status=result["status"]
            )
        else:
            # Fallback to mock service
            mock_result = await generate_service.generate_code(
                language=request.language,
                description=request.description
            )
            
            return CodeGenerateResponse(**mock_result)
        
    except ValueError as e:
        logger.error(f"Validation error in code generation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the generate service.
    """
    return {
        "status": "healthy",
        "service": "generate",
        "openai_configured": openai_service.is_configured()
    }
