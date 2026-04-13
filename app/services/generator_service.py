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

    def _validate_files(self, files: Dict[str, str], component_type: str, project_name: str) -> tuple[bool, List[str]]:
        """
        Validate that generated files are complete and non-empty.
        Returns (is_valid, list_of_issues)
        """
        issues = []
        
        if not files or not isinstance(files, dict):
            issues.append(f"{component_type}: No files generated or invalid format")
            return False, issues
        
        if len(files) == 0:
            issues.append(f"{component_type}: Empty file list generated")
            return False, issues
        
        # Check minimum file counts
        min_files = 10 if component_type == "frontend" else 12
        if len(files) < min_files:
            issues.append(f"{component_type}: Only {len(files)} files generated (minimum {min_files} required)")
        
        # Check for empty or placeholder content
        empty_files = []
        placeholder_patterns = ["TODO", "FIXME", "pass", "# Your implementation here", "// Your implementation here"]
        
        for file_path, content in files.items():
            if not content or content.strip() == "":
                empty_files.append(file_path)
            else:
                # Check for placeholder patterns
                content_lower = content.lower()
                for pattern in placeholder_patterns:
                    if pattern.lower() in content_lower and len(content) < 200:
                        empty_files.append(f"{file_path} (appears to be placeholder)")
                        break
        
        if empty_files:
            issues.append(f"{component_type}: {len(empty_files)} files are empty or contain placeholders: {', '.join(empty_files[:5])}")
        
        # Check for required file patterns
        if component_type == "frontend":
            required_patterns = ["App.tsx", "package.json", "main.tsx"]
            for pattern in required_patterns:
                if not any(pattern in path for path in files.keys()):
                    issues.append(f"{component_type}: Missing required file pattern: {pattern}")
        elif component_type == "backend":
            required_patterns = ["main.py", "requirements.txt", "models"]
            for pattern in required_patterns:
                if not any(pattern in path for path in files.keys()):
                    issues.append(f"{component_type}: Missing required file pattern: {pattern}")
        
        return len(issues) == 0, issues

    async def _generate_component(self, project_name: str, plan: Dict[str, Any], component_type: str, max_retries: int = 2) -> Dict[str, str]:
        """Generic component generation logic with validation and retry."""
        logger.info(f"[GENERATOR] Starting {component_type} generation for: {project_name}")
        
        if component_type == "frontend":
            prompt = get_frontend_prompt(project_name, plan)
        else:
            prompt = get_backend_prompt(project_name, plan)
            
        system_instruction = WEB_DEV_GENERATOR_PROMPT
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"[GENERATOR] Attempt {attempt + 1}/{max_retries + 1} for {component_type}...")
                logger.info(f"[GENERATOR] Prompt length: {len(prompt)} characters")
                
                files = await self.ai.generate_json(prompt, system_instruction)
                logger.info(f"[GENERATOR] AI returned data type: {type(files)}")
                logger.info(f"[GENERATOR] AI returned keys: {list(files.keys()) if isinstance(files, dict) else 'Not a dict'}")
                
                if not files or not isinstance(files, dict):
                    logger.warning(f"[GENERATOR] {component_type} returned invalid data on attempt {attempt + 1}")
                    if attempt < max_retries:
                        continue
                    else:
                        raise ValueError(f"AI generation failed to return valid files after {max_retries + 1} attempts")
                
                logger.info(f"[GENERATOR] Generated {len(files)} files on attempt {attempt + 1}")
                
                # Validate the generated files
                is_valid, issues = self._validate_files(files, component_type, project_name)
                
                if not is_valid:
                    logger.warning(f"[GENERATOR] Validation failed on attempt {attempt + 1}: {issues}")
                    if attempt < max_retries:
                        # Add more specific instructions for retry
                        prompt += f"\n\nRETRY INSTRUCTIONS: Your previous generation had these issues: {', '.join(issues)}. Please fix these issues and generate ALL required files with COMPLETE, WORKING code."
                        continue
                    else:
                        # Log all issues but still return the files (better than nothing)
                        logger.error(f"[GENERATOR] Validation failed after all retries: {issues}")
                        for issue in issues:
                            logger.warning(f"[GENERATOR] - {issue}")
                
                logger.info(f"[GENERATOR] Successfully generated {component_type} with {len(files)} files")
                return files
                
            except Exception as e:
                logger.error(f"[GENERATOR] {component_type} generation failed on attempt {attempt + 1}: {e}", exc_info=True)
                if attempt < max_retries:
                    continue
                else:
                    raise ValueError(f"AI generation error for {component_type} after {max_retries + 1} attempts: {str(e)}")

    async def generate_code(self, plan: Dict[str, Any], components: List[str] = None) -> Dict[str, Any]:
        """
        Generate full code files based on the planner JSON.
        """
        if components is None:
            components = ['frontend', 'backend']
        
        project_name = plan.get("project_name", "Generated Project")
        generated_code = {}
        validation_issues = []
        
        try:
            logger.info(f"Starting professional code generation for: {project_name}")
            
            for component in components:
                if component in ['frontend', 'backend']:
                    files = await self._generate_component(project_name, plan, component)
                    
                    # Final validation
                    is_valid, issues = self._validate_files(files, component, project_name)
                    if not is_valid:
                        validation_issues.extend(issues)
                        logger.warning(f"[GENERATOR] Final validation issues for {component}: {issues}")
                    
                    generated_code[component] = files
            
            total_files = sum(len(files) for files in generated_code.values())
            logger.info(f"[GENERATOR] Total files generated: {total_files}")
            
            result = {
                "status": "success",
                "project_name": project_name,
                "generated_at": datetime.now().isoformat(),
                "files": generated_code,
                "total_files": total_files
            }
            
            if validation_issues:
                result["validation_warnings"] = validation_issues
                logger.warning(f"[GENERATOR] Generation completed with {len(validation_issues)} validation warnings")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in professional code generation: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "files": generated_code,
                "total_files": sum(len(files) for files in generated_code.values()),
                "validation_issues": validation_issues
            }
    
    def get_supported_components(self) -> List[str]:
        """Get list of supported components for generation."""
        return ['frontend', 'backend']
