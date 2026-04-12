import logging
import json
import os
import asyncio
from typing import Dict, Any, List, Optional
from app.config.settings import settings

try:
    from google import genai
    GENAI_IMPORT_ERROR = None
except Exception as exc:
    genai = None
    GENAI_IMPORT_ERROR = exc

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.gemini_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        
        self.gemini_configured = False
        self.gemini_client = None
        
        # Configure Gemini
        if self.gemini_key:
            if genai is None:
                logger.error(
                    f"AIService: google-genai import failed: {GENAI_IMPORT_ERROR}. "
                    "Install dependency: google-genai"
                )
                return
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_key)
                self.gemini_configured = True
                logger.info("AIService: Gemini configured with new API")
            except Exception as e:
                logger.error(f"AIService: Failed to configure Gemini: {e}")

    async def generate_json(self, prompt: str, system_instruction: str = None) -> Dict[str, Any]:
        """Generate structured JSON response."""
        # Use Gemini only
        if self.gemini_configured:
            try:
                return await self._generate_gemini_json(prompt, system_instruction)
            except Exception as e:
                error_str = str(e)
                # Check if it's a quota/rate limit error
                if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                    logger.warning(f"Gemini quota exceeded: {e}")
                    raise ValueError(f"Gemini API quota exceeded. Please add billing to your Gemini account at https://console.cloud.google.com/billing")
                # For other errors, re-raise
                raise
        else:
            if genai is None:
                raise ValueError(
                    "Gemini SDK not installed. Install 'google-genai' and redeploy backend."
                )
            raise ValueError("Gemini not configured. Please check your API key.")

    async def _generate_gemini_json(self, prompt: str, system_instruction: str = None) -> Dict[str, Any]:
        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            # Adding JSON instruction to ensure output
            full_prompt += "\n\nIMPORTANT: Output MUST be a valid JSON object. No markdown, no triple backticks."
            
            # Run synchronous Gemini call in thread pool with timeout using new API
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.gemini_client.models.generate_content,
                    model='gemini-3-flash-preview',
                    contents=full_prompt,
                    config={
                        'response_mime_type': 'application/json'
                    }
                ),
                timeout=120.0  # 120 second timeout for proper research
            )
            return json.loads(response.text)
        except asyncio.TimeoutError:
            logger.error("Gemini JSON generation timed out after 120 seconds")
            raise ValueError("Gemini generation timed out. Please try again.")
        except Exception as e:
            logger.error(f"Gemini JSON generation failed: {e}")
            # Fallback for old models or issues
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.gemini_client.models.generate_content,
                        model='gemini-3-flash-preview',
                        contents=full_prompt
                    ),
                    timeout=60.0
                )
                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                return json.loads(text)
            except asyncio.TimeoutError:
                logger.error("Gemini fallback generation timed out")
                raise ValueError("Gemini generation timed out. Please try again.")
            except:
                raise ValueError(f"Gemini failed to generate valid JSON: {str(e)}")

ai_service = AIService()
