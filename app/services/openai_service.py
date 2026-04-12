from typing import Dict, Any, Optional
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_IMPORT_ERROR = None
except Exception as exc:
    genai = None
    GEMINI_IMPORT_ERROR = exc


class OpenAIService:
    def __init__(self):
        self.api_key = settings.gemini_api_key or settings.openai_api_key
        self.use_gemini = False
        
        if self.api_key and (self.api_key.startswith("AIza") or "GEMINI" in settings.gemini_api_key):
            if genai is None:
                logger.error(f"google.generativeai import failed: {GEMINI_IMPORT_ERROR}")
                return
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.use_gemini = True
                logger.info("OpenAIService Bridge: Using Gemini API")
            except Exception as e:
                logger.error(f"Failed to configure Gemini bridge: {e}")
        else:
            logger.warning("No API key configured for AI service bridge")
    
    async def generate_response(
        self, 
        prompt: str, 
        model: str = "gpt-3.5-turbo",
        max_tokens: Optional[int] = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate a response using OpenAI API.
        
        Args:
            prompt: User prompt/question
            model: OpenAI model to use
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0.0-1.0)
            
        Returns:
            Dictionary containing the response and metadata
        """
        if not self.use_gemini:
            raise ValueError("Gemini bridge not configured. Please check your API key.")
        
        try:
            logger.info("Generating response via Gemini bridge")
            
            response = self.model.generate_content(prompt)
            content = response.text
            
            return {
                "content": content,
                "model": "gemini-1.5-flash",
                "usage": {"total_tokens": 0},
                "finish_reason": "STOP",
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Gemini bridge error: {str(e)}")
            raise ValueError(f"AI error: {str(e)}")
    
    async def generate_code(
        self,
        description: str,
        language: str = "python",
        model: str = "gpt-3.5-turbo",
        max_tokens: Optional[int] = 1500
    ) -> Dict[str, Any]:
        """
        Generate code using OpenAI API.
        
        Args:
            description: Description of the code to generate
            language: Programming language
            model: OpenAI model to use
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary containing the generated code and metadata
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please check your API key.")
        
        code_prompt = f"""
        Generate {language} code for the following description:
        
        Description: {description}
        
        Please provide clean, well-commented code that follows best practices.
        Include necessary imports and make the code functional.
        """
        
        try:
            logger.info(f"Generating {language} code with model: {model}")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"You are a helpful {language} programmer assistant."},
                    {"role": "user", "content": code_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3  # Lower temperature for more deterministic code
            )
            
            content = response.choices[0].message.content
            usage = response.usage
            
            return {
                "code": content,
                "language": language,
                "description": description,
                "model": model,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason,
                "status": "success"
            }
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error in code generation: {str(e)}")
            raise ValueError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI code generation: {str(e)}")
            raise ValueError(f"Unexpected error: {str(e)}")
    
    def is_configured(self) -> bool:
        """Check if service is properly configured."""
        return self.use_gemini
