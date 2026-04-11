import logging
import json
import os
from openai import OpenAI
from app.config.settings import settings

logger = logging.getLogger(__name__)


from typing import Dict, Any, List, Optional
import logging
import json
from app.services.ai_service import ai_service
from app.services.prompts import WEB_DEV_PLANNER_PROMPT

logger = logging.getLogger(__name__)


class PlannerService:
    def __init__(self):
        self.ai = ai_service

    async def create_project_plan(self, user_prompt: str) -> Dict[str, Any]:
        """Create a structured project plan from user prompt."""
        logger.info(f"[PLANNER] Starting plan creation for: {user_prompt[:100]}...")
        
        system_instruction = WEB_DEV_PLANNER_PROMPT
        
        planning_prompt = f"""
        Analyze the following user request and create a detailed, professional project plan.
        USER REQUEST: {user_prompt}
        
        The plan should include:
        - project_name
        - architecture_summary
        - features (list of strings)
        - database_schema (list of objects with name and fields)
        - frontend_components (list of objects with name and purpose)
        - backend_endpoints (list of strings)
        - design_system (details about colors, fonts, and animation style)
        - implementation_roadmap (steps to build)
        """
        
        try:
            logger.info("[PLANNER] Calling AI service for JSON generation...")
            plan = await self.ai.generate_json(planning_prompt, system_instruction)
            logger.info(f"[PLANNER] Successfully generated plan with {len(plan)} keys")
            return {
                "plan": plan,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"[PLANNER] Planning failed: {e}", exc_info=True)
            raise ValueError(f"Planning Error: {str(e)}")

    async def create_simple_plan(self, user_prompt: str, focus_area: str = "general") -> Dict[str, Any]:
        """Simplified planning for quick prototyping."""
        return await self.create_project_plan(f"{user_prompt} (Focus on: {focus_area})")

    def is_configured(self) -> bool:
        """Check if service is properly configured."""
        return self.ai.gemini_configured or self.ai.openai_configured

