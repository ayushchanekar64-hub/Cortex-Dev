from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from app.services.tester_service import TesterService

router = APIRouter(prefix="/tester", tags=["tester"])
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class TestGenerationRequest(BaseModel):
    files: Dict[str, str] = Field(..., description="Dictionary mapping filenames to code content")
    test_framework: Optional[str] = Field(None, description="Override default test framework")

class TestResult(BaseModel):
    status: str
    tests_run: int
    failures: int
    errors: int
    output: str

class TestSummary(BaseModel):
    status: str
    language: Optional[str] = None
    test_filename: Optional[str] = None
    functions_found: int = 0
    classes_found: int = 0
    components_found: int = 0
    endpoints_found: int = 0
    reason: Optional[str] = None

class TestGenerationResponse(BaseModel):
    status: str
    generated_tests: Dict[str, str] = Field(..., description="Dictionary mapping test filenames to test code")
    test_summary: Dict[str, TestSummary]
    total_files_processed: int
    total_tests_generated: int
    generated_at: str

class APIValidationRequest(BaseModel):
    api_base_url: str = Field("http://localhost:8000", description="Base URL of the API to test")
    custom_endpoints: Optional[List[Dict[str, Any]]] = Field(None, description="Custom endpoints to test")

class APIEndpointResult(BaseModel):
    status_code: Optional[int] = None
    expected_status: List[int]
    passed: bool
    response_time: Optional[float] = None
    response_size: Optional[int] = None
    error: Optional[str] = None

class APIValidationResponse(BaseModel):
    status: str
    api_base_url: str
    total_endpoints_tested: int
    endpoints_passed: int
    endpoints_failed: int
    success_rate: float
    test_results: Dict[str, APIEndpointResult]
    tested_at: str

class TestExecutionRequest(BaseModel):
    test_files: Dict[str, str] = Field(..., description="Dictionary mapping test filenames to test code")
    test_framework: Optional[str] = Field(None, description="Test framework to use")

class TestExecutionResponse(BaseModel):
    status: str
    total_test_files: int
    total_tests_run: int
    total_failures: int
    total_errors: int
    success_rate: float
    test_results: Dict[str, TestResult]
    run_at: str

# Initialize service
tester_service = TesterService()


@router.post("/generate", response_model=TestGenerationResponse)
async def generate_tests(request: TestGenerationRequest):
    """
    Generate test cases for provided code files.
    """
    try:
        logger.info(f"Generating tests for {len(request.files)} files")
        
        if not request.files:
            raise HTTPException(status_code=400, detail="No files provided for test generation")
        
        result = await tester_service.generate_tests(request.files)
        
        if result["status"] != "completed":
            raise HTTPException(status_code=500, detail="Test generation failed")
        
        return TestGenerationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating tests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/validate-api", response_model=APIValidationResponse)
async def validate_api(request: APIValidationRequest):
    """
    Validate API endpoints by making HTTP requests.
    """
    try:
        logger.info(f"Validating API endpoints at {request.api_base_url}")
        
        result = await tester_service.validate_api_endpoints(request.api_base_url)
        
        if result["status"] != "completed":
            raise HTTPException(status_code=500, detail="API validation failed")
        
        return APIValidationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/run-tests", response_model=TestExecutionResponse)
async def run_tests(request: TestExecutionRequest):
    """
    Run generated test files and return results.
    """
    try:
        logger.info(f"Running {len(request.test_files)} test files")
        
        if not request.test_files:
            raise HTTPException(status_code=400, detail="No test files provided")
        
        result = await tester_service.run_tests(request.test_files)
        
        if result["status"] != "completed":
            raise HTTPException(status_code=500, detail="Test execution failed")
        
        return TestExecutionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/sample-code")
async def get_sample_code():
    """
    Get sample code files for testing the tester agent.
    """
    sample_files = {
        "main.py": '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str
    price: float

items = {}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

@app.post("/items/")
async def create_item(item: Item):
    item_id = len(items) + 1
    items[item_id] = item.dict()
    return {"item_id": item_id, "item": item}
''',
        
        "utils.js": '''
// Utility functions for calculations

export const add = (a, b) => {
    return a + b;
};

export const multiply = (a, b) => {
    return a * b;
};

export const factorial = (n) => {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
};

export const isEven = (num) => {
    return num % 2 === 0;
};
''',
        
        "Button.tsx": '''
import React from 'react';

interface ButtonProps {
    label: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary';
    disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ 
    label, 
    onClick, 
    variant = 'primary', 
    disabled = false 
}) => {
    const baseClasses = 'px-4 py-2 rounded font-medium transition-colors';
    const variantClasses = variant === 'primary' 
        ? 'bg-blue-500 text-white hover:bg-blue-600' 
        : 'bg-gray-200 text-gray-800 hover:bg-gray-300';
    
    return (
        <button
            className={`${baseClasses} ${variantClasses}`}
            onClick={onClick}
            disabled={disabled}
        >
            {label}
        </button>
    );
};

export default Button;
'''
    }
    
    return {
        "sample_files": sample_files,
        "description": "Sample code files for testing the Tester Agent",
        "languages": ["Python", "JavaScript", "TypeScript"],
        "expected_tests": [
            "Unit tests for Python FastAPI endpoints",
            "Utility function tests for JavaScript",
            "React component tests for TypeScript"
        ]
    }


@router.get("/sample-tests")
async def get_sample_tests():
    """
    Get sample test files generated by the tester agent.
    """
    sample_tests = {
        "test_main.py": '''
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestRoot:
    def test_root_endpoint(self):
        """Test that root endpoint returns correct response."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

class TestItems:
    def test_read_existing_item(self):
        """Test reading an existing item."""
        # First create an item
        item_data = {"name": "Test Item", "description": "A test item", "price": 10.99}
        create_response = client.post("/items/", json=item_data)
        assert create_response.status_code == 200
        
        item_id = create_response.json()["item_id"]
        
        # Then read it
        response = client.get(f"/items/{item_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Item"
    
    def test_read_nonexistent_item(self):
        """Test reading a non-existent item returns 404."""
        response = client.get("/items/999")
        assert response.status_code == 404
    
    def test_create_item(self):
        """Test creating a new item."""
        item_data = {"name": "New Item", "description": "A new test item", "price": 15.99}
        response = client.post("/items/", json=item_data)
        assert response.status_code == 200
        assert response.json()["item"]["name"] == "New Item"
''',
        
        "utils.test.js": '''
// Jest tests for utility functions

const { add, multiply, factorial, isEven } = require('./utils');

describe('add', () => {
    test('should add two positive numbers', () => {
        expect(add(2, 3)).toBe(5);
    });
    
    test('should handle negative numbers', () => {
        expect(add(-2, 3)).toBe(1);
    });
    
    test('should handle zero', () => {
        expect(add(0, 5)).toBe(5);
    });
});

describe('multiply', () => {
    test('should multiply two positive numbers', () => {
        expect(multiply(3, 4)).toBe(12);
    });
    
    test('should multiply by zero', () => {
        expect(multiply(5, 0)).toBe(0);
    });
});

describe('factorial', () => {
    test('should calculate factorial of 5', () => {
        expect(factorial(5)).toBe(120);
    });
    
    test('should return 1 for factorial of 1', () => {
        expect(factorial(1)).toBe(1);
    });
});

describe('isEven', () => {
    test('should return true for even numbers', () => {
        expect(isEven(4)).toBe(true);
    });
    
    test('should return false for odd numbers', () => {
        expect(isEven(3)).toBe(false);
    });
});
''',
        
        "Button.test.tsx": '''
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Button from './Button';

describe('Button', () => {
    test('renders with label', () => {
        render(<Button label="Click me" onClick={() => {}} />);
        expect(screen.getByText('Click me')).toBeInTheDocument();
    });
    
    test('calls onClick when clicked', () => {
        const handleClick = jest.fn();
        render(<Button label="Click me" onClick={handleClick} />);
        
        fireEvent.click(screen.getByText('Click me'));
        expect(handleClick).toHaveBeenCalledTimes(1);
    });
    
    test('applies primary variant styles by default', () => {
        render(<Button label="Primary" onClick={() => {}} />);
        const button = screen.getByText('Primary');
        expect(button).toHaveClass('bg-blue-500');
    });
    
    test('applies secondary variant styles', () => {
        render(<Button label="Secondary" onClick={() => {}} variant="secondary" />);
        const button = screen.getByText('Secondary');
        expect(button).toHaveClass('bg-gray-200');
    });
    
    test('is disabled when disabled prop is true', () => {
        render(<Button label="Disabled" onClick={() => {}} disabled={true} />);
        const button = screen.getByText('Disabled');
        expect(button).toBeDisabled();
    });
});
'''
    }
    
    return {
        "sample_tests": sample_tests,
        "description": "Sample test files generated by the Tester Agent",
        "test_frameworks": ["pytest", "Jest"],
        "test_types": ["unit tests", "component tests", "API tests"]
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the tester service.
    """
    return {
        "status": "healthy",
        "service": "tester",
        "supported_languages": tester_service.get_supported_languages()
    }


@router.get("/frameworks")
async def get_supported_frameworks():
    """
    Get list of supported test frameworks by language.
    """
    return {
        "supported_frameworks": {
            "python": ["pytest"],
            "javascript": ["Jest"],
            "typescript": ["Jest"]
        },
        "description": "Test frameworks supported by the Tester Agent"
    }
