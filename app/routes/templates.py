from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
from ..templates.templates import get_template, get_all_templates, merge_template_with_generation

router = APIRouter(prefix="/templates", tags=["templates"])


class TemplateRequest(BaseModel):
    template_id: str
    prompt: str
    generated_files: Dict[str, str] = {}


@router.get("/")
async def get_templates():
    """Get all available templates"""
    templates = get_all_templates()
    return {
        "templates": templates,
        "count": len(templates)
    }


@router.get("/{template_id}")
async def get_template_by_id(template_id: str):
    """Get a specific template by ID"""
    template = get_template(template_id)
    if not template:
        return {"error": "Template not found"}
    return template


@router.post("/merge")
async def merge_template(request: TemplateRequest):
    """Merge template with AI-generated files"""
    template = get_template(request.template_id)
    if not template:
        return {"error": "Template not found"}
    
    merged_files = merge_template_with_generation(template, request.generated_files, request.prompt)
    
    return {
        "success": True,
        "merged_files": merged_files,
        "template_name": template["name"],
        "file_count": len(merged_files)
    }
