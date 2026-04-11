WEB_DEV_PLANNER_PROMPT = """
You are a web development expert. Create a detailed project plan for the given request.
Include: project_name, features (with descriptions), frontend_components, backend_endpoints, database_schema, tech_stack.
Make the plan specific to the user's requirements, not generic.
"""

WEB_DEV_GENERATOR_PROMPT = """
You are a senior full-stack developer. Generate complete, working, production-ready code files based on the project plan.
Every file must be fully functional with no placeholder code or comments like "TODO".
Write unique, specific code that matches the project requirements exactly.
Do not use generic templates - write code specifically for this project.
CRITICAL: You MUST generate at least 3-5 files with actual code content.
"""

def get_frontend_prompt(project_name, plan):
    return f"""
Build a React frontend for "{project_name}".

Project Plan:
{plan}

CRITICAL INSTRUCTIONS:
1. You MUST generate actual code files - no empty files or placeholders
2. Each file must have complete, working code
3. Return at least 4-5 files with full content
4. Do NOT skip any file generation
5. Every file must be properly formatted and ready to use

Generate these specific files with COMPLETE code:
1. frontend/src/App.tsx - Full React app with proper imports, state, and JSX
2. frontend/src/components/{project_name.lower().replace(' ', '')}Main.tsx - Complete component with props and state
3. frontend/src/components/Header.tsx - Full header component with navigation
4. frontend/src/styles/globals.css - Complete CSS styles for the project
5. frontend/package.json - Full package.json with all dependencies

IMPORTANT: The JSON response MUST have file paths as keys and the COMPLETE code as string values.
Example format:
{{
  "frontend/src/App.tsx": "import React from 'react'\\nfunction App() {{ return <div>Hello</div> }}\\nexport default App",
  "frontend/src/components/Main.tsx": "import React from 'react'\\nexport default function Main() {{ return <div>Main</div> }}",
  ...
}}

DO NOT return empty objects or missing files. Generate ALL files with full code.
"""

def get_backend_prompt(project_name, plan):
    return f"""
Build a FastAPI backend for "{project_name}".

Project Plan:
{plan}

CRITICAL INSTRUCTIONS:
1. You MUST generate actual code files - no empty files or placeholders
2. Each file must have complete, working code
3. Return at least 4-5 files with full content
4. Do NOT skip any file generation
5. Every file must be properly formatted and ready to use

Generate these specific files with COMPLETE code:
1. backend/main.py - Full FastAPI app with imports, app instance, and routes
2. backend/app/models.py - Complete SQLAlchemy models with all fields
3. backend/app/schemas.py - Full Pydantic schemas for all models
4. backend/app/routes/api.py - Complete API routes with all endpoints
5. backend/requirements.txt - Full list of all required dependencies

IMPORTANT: The JSON response MUST have file paths as keys and the COMPLETE code as string values.
Example format:
{{
  "backend/main.py": "from fastapi import FastAPI\\napp = FastAPI()\\n@app.get('/')\\ndef home(): return {{'message': 'Hello'}}",
  "backend/app/models.py": "from sqlalchemy import Column, Integer, String\\n...",
  ...
}}

DO NOT return empty objects or missing files. Generate ALL files with full code.
"""
