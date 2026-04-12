from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime
from app.services.ai_service import ai_service
from app.services.prompts import WEB_DEV_GENERATOR_PROMPT, get_frontend_prompt, get_backend_prompt

logger = logging.getLogger(__name__)


class GeneratorService:
    def __init__(self):
        self.ai = ai_service

    async def _generate_component(self, project_name: str, plan: Dict[str, Any], component_type: str) -> Dict[str, str]:
        """Generic component generation logic."""
        logger.info(f"[GENERATOR] Starting {component_type} generation for: {project_name}")
        
        if component_type == "frontend":
            prompt = get_frontend_prompt(project_name, plan)
        else:
            prompt = get_backend_prompt(project_name, plan)
            
        system_instruction = WEB_DEV_GENERATOR_PROMPT
        
        try:
            logger.info(f"[GENERATOR] Calling AI service for {component_type}...")
            logger.info(f"[GENERATOR] Prompt length: {len(prompt)} characters")
            files = await self.ai.generate_json(prompt, system_instruction)
            logger.info(f"[GENERATOR] AI returned data type: {type(files)}")
            logger.info(f"[GENERATOR] AI returned keys: {list(files.keys()) if isinstance(files, dict) else 'Not a dict'}")
            logger.info(f"[GENERATOR] Successfully generated {component_type} with {len(files)} files")
            
            if not files or len(files) == 0:
                logger.warning(f"[GENERATOR] {component_type} returned empty files! Response: {files}")
            
            return files
        except Exception as e:
            logger.error(f"[GENERATOR] {component_type} generation failed: {e}", exc_info=True)
            raise ValueError(f"AI generation error for {component_type}: {str(e)}")

    async def generate_code(self, plan: Dict[str, Any], components: List[str] = None) -> Dict[str, Any]:
        """
        Generate full code files based on the planner JSON.
        """
        if components is None:
            components = ['frontend', 'backend']
        
        project_name = plan.get("project_name", "Generated Project")
        generated_code = {}
        
        try:
            logger.info(f"Starting professional code generation for: {project_name}")
            
            for component in components:
                if component in ['frontend', 'backend']:
                    files = await self._generate_component(project_name, plan, component)
                    generated_code[component] = files
            
            return {
                "status": "success",
                "project_name": project_name,
                "generated_at": datetime.now().isoformat(),
                "files": generated_code,
                "total_files": sum(len(files) for files in generated_code.values())
            }
            
        except Exception as e:
            logger.error(f"Error in professional code generation: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "files": {},
                "total_files": 0
            }
    
    def get_supported_components(self) -> List[str]:
        """Get list of supported components for generation."""
        return ['frontend', 'backend']
