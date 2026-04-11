# Cortex-Dev - FastAPI Backend

A clean, scalable FastAPI backend for an AI SaaS application called "Cortex-Dev".

## Project Structure

```
Cortex-Dev/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI application
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py      # Environment configuration
│   ├── routes/
│   │   ├── __init__.py
│   │   └── generate.py      # Generate endpoints
│   └── services/
│       ├── __init__.py
│       └── generate_service.py  # Business logic
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md              # This file
```

## Features

- ✅ Clean, modular architecture
- ✅ Environment variable configuration
- ✅ CORS support
- ✅ `/generate` endpoint for content generation
- ✅ `/generate/code` endpoint for code generation
- ✅ Health check endpoints
- ✅ Proper logging
- ✅ Pydantic models for validation

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp .env.example .env
```

Edit the `.env` file with your specific settings:
- Set `DEBUG` to `False` for production
- Update `ALLOWED_ORIGINS` for your frontend domains
- Add your AI API keys if needed

### 3. Run the Application

#### Development Mode (with auto-reload):
```bash
python -m app.main
```

#### Production Mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Root Endpoint
- **GET** `/` - Welcome message and app info

### Health Check
- **GET** `/health` - Application health status

### Generate Endpoints
- **POST** `/generate/` - Generate content from prompt
  ```json
  {
    "prompt": "Your prompt here",
    "options": {
      "temperature": 0.7,
      "max_tokens": 1000
    }
  }
  ```

- **POST** `/generate/code` - Generate code from description
  ```json
  {
    "language": "python",
    "description": "Create a function that sorts a list"
  }
  ```

- **GET** `/generate/health` - Generate service health check

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Configuration

The application uses the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | "Cortex-Dev" | Application name |
| `DEBUG` | `False` | Enable debug mode |
| `HOST` | "0.0.0.0" | Server host |
| `PORT` | `8000` | Server port |
| `ALLOWED_ORIGINS` | `["http://localhost:3000", "http://localhost:8080"]` | CORS allowed origins |
| `OPENAI_API_KEY` | `""` | OpenAI API key (for future AI integration) |

## Development Notes

- The service layer (`app/services/`) contains business logic
- Routes (`app/routes/`) handle HTTP requests and responses
- Configuration (`app/config/`) manages environment variables
- The application follows FastAPI best practices with proper separation of concerns

## Future Enhancements

- Add AI model integration (OpenAI, Anthropic, etc.)
- Implement authentication and authorization
- Add database integration
- Implement rate limiting
- Add comprehensive error handling
- Add unit and integration tests
