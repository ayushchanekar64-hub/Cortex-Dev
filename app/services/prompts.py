WEB_DEV_PLANNER_PROMPT = """
You are a senior full-stack architect. Create a DETAILED, COMPREHENSIVE project plan for the given request.
Include: project_name, features (with detailed descriptions), frontend_components (list ALL components needed), 
backend_endpoints (list ALL API routes with methods), database_schema (ALL tables with fields and relationships), 
tech_stack (specific versions), folder_structure (complete tree structure).
Make the plan specific to the user's requirements, not generic.
"""

WEB_DEV_GENERATOR_PROMPT = """
You are a senior full-stack developer. Generate COMPLETE, PRODUCTION-READY code files based on the project plan.
EVERY file must be fully functional with NO placeholder code, NO "TODO" comments, NO pseudo-code.
Write unique, specific code that matches the project requirements exactly.
CRITICAL: You MUST generate ALL files for a complete project structure - minimum 10-15 files with actual code content.
"""

def get_frontend_prompt(project_name, plan):
    return f"""
Build a COMPLETE, PRODUCTION-READY React/Next.js frontend for "{project_name}".

Project Plan:
{plan}

CRITICAL INSTRUCTIONS:
1. You MUST generate ALL required files for a complete React project - NO exceptions
2. Each file must have COMPLETE, WORKING code - no placeholders, no TODOs, no incomplete implementations
3. Return MINIMUM 10-15 files with full, production-ready content
4. Do NOT skip any file generation - generate ALL files listed below
5. Every file must be properly formatted, include error handling, and be ready to deploy
6. Include proper TypeScript types, React hooks, state management, and API integration
7. Add proper styling with Tailwind CSS or CSS modules
8. Include proper routing with React Router

Generate these specific files with COMPLETE code:

CORE FILES:
1. frontend/src/App.tsx - Full React app with routing, providers, and layout
2. frontend/src/main.tsx - Entry point with React 18 render
3. frontend/src/index.css - Global styles with Tailwind directives
4. frontend/package.json - Complete with ALL dependencies (react, react-dom, react-router-dom, axios, etc.)
5. frontend/vite.config.ts - Complete Vite configuration
6. frontend/tsconfig.json - Complete TypeScript configuration
7. frontend/index.html - HTML entry point

COMPONENTS (at least 6-8 components):
8. frontend/src/components/Layout/Layout.tsx - Main layout with header and sidebar
9. frontend/src/components/Layout/Header.tsx - Header with navigation and user menu
10. frontend/src/components/Layout/Sidebar.tsx - Sidebar with navigation links
11. frontend/src/components/{project_name.lower().replace(' ', '')}Dashboard.tsx - Main dashboard component
12. frontend/src/components/{project_name.lower().replace(' ', '')}List.tsx - List view component with pagination
13. frontend/src/components/{project_name.lower().replace(' ', '')}Form.tsx - Form component with validation
14. frontend/src/components/{project_name.lower().replace(' ', '')}Detail.tsx - Detail view component
15. frontend/src/components/common/Button.tsx - Reusable button component
16. frontend/src/components/common/Input.tsx - Reusable input component
17. frontend/src/components/common/Modal.tsx - Reusable modal component

SERVICES:
18. frontend/src/services/api.ts - Complete API service with axios, base URL, interceptors
19. frontend/src/services/authService.ts - Complete authentication service (login, logout, token management)
20. frontend/src/services/{project_name.lower().replace(' ', '')}Service.ts - Service for specific project features

HOOKS:
21. frontend/src/hooks/useAuth.ts - Custom hook for authentication
22. frontend/src/hooks/useApi.ts - Custom hook for API calls
23. frontend/src/hooks/use{project_name.replace(' ', '')}s.ts - Custom hook for project data

TYPES:
24. frontend/src/types/index.ts - Complete TypeScript interfaces for all data models

CONTEXT:
25. frontend/src/context/AuthContext.tsx - Complete authentication context with provider

PAGES (if using Next.js):
26. frontend/src/pages/_app.tsx - Next.js app wrapper
27. frontend/src/pages/index.tsx - Home page

IMPORTANT: The JSON response MUST have file paths as keys and the COMPLETE code as string values.
Example format:
{{
  "frontend/src/App.tsx": "import React from 'react'\\nimport {{ BrowserRouter }} from 'react-router-dom'\\n...FULL CODE...",
  "frontend/src/components/Layout/Header.tsx": "import React from 'react'\\n...FULL CODE...",
  ...
}}

DO NOT return empty objects or missing files. Generate ALL files with FULL, PRODUCTION-READY code.
Every file must be complete and ready to run without modifications.
"""

def get_backend_prompt(project_name, plan):
    return f"""
Build a COMPLETE, PRODUCTION-READY FastAPI backend for "{project_name}".

Project Plan:
{plan}

CRITICAL INSTRUCTIONS:
1. You MUST generate ALL required files for a complete FastAPI project - NO exceptions
2. Each file must have COMPLETE, WORKING code - no placeholders, no TODOs, no incomplete implementations
3. Return MINIMUM 12-18 files with full, production-ready content
4. Do NOT skip any file generation - generate ALL files listed below
5. Every file must be properly formatted, include error handling, validation, and be ready to deploy
6. Include proper database models, Pydantic schemas, API routes, authentication (JWT), middleware
7. Add proper logging, configuration management, and environment variable handling
8. Include database migrations setup and example seed data

Generate these specific files with COMPLETE code:

CORE FILES:
1. backend/main.py - Complete FastAPI app with CORS, middleware, routers, startup/shutdown events
2. backend/requirements.txt - Complete with ALL dependencies (fastapi, uvicorn, sqlalchemy, pydantic, python-jose, passlib, etc.)
3. backend/.env.example - Environment variables template
4. backend/README.md - Setup and deployment instructions

CONFIGURATION:
5. backend/app/config/settings.py - Complete settings with Pydantic settings, environment variables
6. backend/app/config/database.py - Complete database configuration with SQLAlchemy session management
7. backend/app/config/__init__.py - Package init

MODELS (at least 3-4 models):
8. backend/app/models/__init__.py - Models package init
9. backend/app/models/user.py - Complete User model with authentication fields
10. backend/app/models/{project_name.lower().replace(' ', '')}.py - Main project model with all fields
11. backend/app/models/base.py - Base model with common fields (id, created_at, updated_at)

SCHEMAS:
12. backend/app/schemas/__init__.py - Schemas package init
13. backend/app/schemas/user.py - Complete user schemas (UserCreate, UserResponse, UserLogin)
14. backend/app/schemas/{project_name.lower().replace(' ', '')}.py - Complete project schemas with validation
15. backend/app/schemas/token.py - Token schemas for JWT authentication

ROUTES/CONTROLLERS:
16. backend/app/routes/__init__.py - Routes package init
17. backend/app/routes/auth.py - Complete authentication routes (register, login, logout, refresh token)
18. backend/app/routes/{project_name.lower().replace(' ', '')}.py - Complete CRUD routes for project
19. backend/app/routes/health.py - Health check endpoint

SERVICES/BUSINESS LOGIC:
20. backend/app/services/__init__.py - Services package init
21. backend/app/services/auth_service.py - Complete auth service with password hashing, JWT token generation
22. backend/app/services/{project_name.lower().replace(' ', '')}_service.py - Complete business logic service

MIDDLEWARE:
23. backend/app/middleware/__init__.py - Middleware package init
24. backend/app/middleware/auth.py - JWT authentication middleware
25. backend/app/middleware/error_handler.py - Global error handling middleware

UTILS:
26. backend/app/utils/__init__.py - Utils package init
27. backend/app/utils/security.py - Password hashing, JWT utilities
28. backend/app/utils/logger.py - Logging configuration

DATABASE:
29. backend/app/database.py - Database initialization and session management
30. backend/alembic.ini - Alembic configuration for migrations
31. backend/alembic/env.py - Alembic environment setup

IMPORTANT: The JSON response MUST have file paths as keys and the COMPLETE code as string values.
Example format:
{{
  "backend/main.py": "from fastapi import FastAPI\\nfrom fastapi.middleware.cors import CORSMiddleware\\n...FULL CODE...",
  "backend/app/models/user.py": "from sqlalchemy import Column, Integer, String...FULL CODE...",
  ...
}}

DO NOT return empty objects or missing files. Generate ALL files with FULL, PRODUCTION-READY code.
Every file must be complete and ready to run without modifications.
"""
