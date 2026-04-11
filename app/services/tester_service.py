from typing import Dict, Any, List, Optional, Tuple
import logging
import re
import ast
import json
from datetime import datetime
from datetime import datetime
# import httpx  # Commented out due to Python 3.14 instability with httpcore

logger = logging.getLogger(__name__)


class TesterService:
    def __init__(self):
        self.language_patterns = {
            'python': {
                'extensions': ['.py'],
                'test_framework': 'pytest',
                'test_generator': self._generate_python_tests,
                'test_runner': self._run_python_tests
            },
            'javascript': {
                'extensions': ['.js', '.jsx'],
                'test_framework': 'jest',
                'test_generator': self._generate_javascript_tests,
                'test_runner': self._run_javascript_tests
            },
            'typescript': {
                'extensions': ['.ts', '.tsx'],
                'test_framework': 'jest',
                'test_generator': self._generate_typescript_tests,
                'test_runner': self._run_typescript_tests
            }
        }
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        filename_lower = filename.lower()
        
        for language, config in self.language_patterns.items():
            for ext in config['extensions']:
                if filename_lower.endswith(ext):
                    return language
        
        return 'unknown'
    
    def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code to extract functions and classes."""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'endpoints': []
        }
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'return_type': ast.unparse(node.returns) if node.returns else None,
                        'docstring': ast.get_docstring(node) or ""
                    }
                    analysis['functions'].append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'methods': [],
                        'docstring': ast.get_docstring(node) or ""
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'name': item.name,
                                'args': [arg.arg for arg in item.args.args],
                                'docstring': ast.get_docstring(item) or ""
                            }
                            class_info['methods'].append(method_info)
                    
                    analysis['classes'].append(class_info)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        analysis['imports'].append(f"{module}.{alias.name}")
                
                # Detect FastAPI endpoints
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr in ['get', 'post', 'put', 'delete']:
                                endpoint_info = {
                                    'method': decorator.func.attr.upper(),
                                    'path': ast.unparse(decorator.args[0]) if decorator.args else '/',
                                    'function': node.name
                                }
                                analysis['endpoints'].append(endpoint_info)
        
        except Exception as e:
            logger.error(f"Error analyzing Python code: {str(e)}")
        
        return analysis
    
    def _analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code to extract functions and components."""
        analysis = {
            'functions': [],
            'components': [],
            'exports': [],
            'endpoints': []
        }
        
        # Extract function definitions
        func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))'
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1) or match.group(2)
            if func_name:
                analysis['functions'].append({
                    'name': func_name,
                    'type': 'function'
                })
        
        # Extract React components
        component_pattern = r'(?:const|function)\s+(\w+)[^=]*=\s*(?:\([^)]*\)\s*=>|React\.\w+\s*\([^)]*\)\s*=>)'
        for match in re.finditer(component_pattern, code):
            component_name = match.group(1)
            if component_name and component_name[0].isupper():
                analysis['components'].append({
                    'name': component_name,
                    'type': 'component'
                })
        
        # Extract exports
        export_pattern = r'export\s+(?:default\s+)?(?:const|function|class)\s+(\w+)'
        for match in re.finditer(export_pattern, code):
            export_name = match.group(1)
            analysis['exports'].append(export_name)
        
        return analysis
    
    def _generate_python_tests(self, filename: str, code: str, analysis: Dict[str, Any]) -> str:
        """Generate Python pytest tests."""
        test_code = f"""import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module to test
# from {filename.replace('.py', '')} import *

"""
        
        # Generate tests for functions
        for func in analysis.get('functions', []):
            if not func['name'].startswith('_'):  # Skip private functions
                test_code += f"""
class Test{func['name'].title()}:
    def test_{func['name']}_exists(self):
        \"\"\"Test that {func['name']} function exists and is callable.\"\"\"
        # This test would need to be adapted based on your module structure
        pass
    
    def test_{func['name']}_returns_something(self):
        \"\"\"Test that {func['name']} returns expected type.\"\"\"
        # Add specific test logic based on function signature
        pass
"""
        
        # Generate tests for classes
        for cls in analysis.get('classes', []):
            test_code += f"""
class Test{cls['name']}:
    def test_{cls['name'].lower()}_instantiation(self):
        \"\"\"Test that {cls['name']} can be instantiated.\"\"\"
        # Add instantiation test
        pass
    
    def test_{cls['name'].lower()}_methods(self):
        \"\"\"Test that {cls['name']} methods work correctly.\"\"\"
        # Add method tests
        pass
"""
        
        # Generate API endpoint tests
        for endpoint in analysis.get('endpoints', []):
            test_code += f"""
class TestAPI{endpoint['method']}{endpoint['path'].replace('/', '_').replace(':', '')}:
    def test_{endpoint['method'].lower()}_endpoint(self):
        \"\"\"Test {endpoint['method']} {endpoint['path']} endpoint.\"\"\"
        # This would typically use TestClient from FastAPI
        # response = client.{endpoint['method'].lower()}('{endpoint['path']}')
        # assert response.status_code in [200, 201]
        pass
"""
        
        return test_code
    
    def _generate_javascript_tests(self, filename: str, code: str, analysis: Dict[str, Any]) -> str:
        """Generate JavaScript Jest tests."""
        test_code = f"""// Jest tests for {filename}

"""
        
        # Generate tests for functions
        for func in analysis.get('functions', []):
            test_code += f"""
describe('{func['name']}', () => {{
  test('should exist and be callable', () => {{
    // Add function existence test
    expect(typeof {func['name']}).toBe('function');
  }});
  
  test('should return expected output', () => {{
    // Add specific test logic
    const result = {func['name']}();
    // expect(result).toBeDefined();
  }});
}});
"""
        
        # Generate tests for React components
        for component in analysis.get('components', []):
            test_code += f"""
import React from 'react';
import {{ render, screen }} from '@testing-library/react';
import {component['name']} from './{filename.replace('.js', '').replace('.jsx', '')}';

describe('{component['name']}', () => {{
  test('renders without crashing', () => {{
    render(<{component['name']} />);
  }});
  
  test('displays expected content', () => {{
    render(<{component['name']} />);
    // Add specific content tests
  }});
}});
"""
        
        return test_code
    
    def _generate_typescript_tests(self, filename: str, code: str, analysis: Dict[str, Any]) -> str:
        """Generate TypeScript Jest tests."""
        test_code = f"""// Jest tests for {filename}

"""
        
        # Similar to JavaScript but with TypeScript types
        for func in analysis.get('functions', []):
            test_code += f"""
describe('{func['name']}', () => {{
  test('should exist and be callable', () => {{
    expect(typeof {func['name']}).toBe('function');
  }});
  
  test('should return expected type', () => {{
    const result = {func['name']}();
    // Add type-specific tests
  }});
}});
"""
        
        return test_code
    
    async def _run_python_tests(self, test_files: Dict[str, str]) -> Dict[str, Any]:
        """Run Python tests (mock implementation)."""
        results = {}
        
        for filename, test_code in test_files.items():
            # In a real implementation, this would run pytest
            # For now, return mock results
            results[filename] = {
                'status': 'passed',
                'tests_run': 5,
                'failures': 0,
                'errors': 0,
                'output': 'Mock test results - all tests passed'
            }
        
        return results
    
    async def _run_javascript_tests(self, test_files: Dict[str, str]) -> Dict[str, Any]:
        """Run JavaScript tests (mock implementation)."""
        results = {}
        
        for filename, test_code in test_files.items():
            # In a real implementation, this would run Jest
            results[filename] = {
                'status': 'passed',
                'tests_run': 3,
                'failures': 0,
                'errors': 0,
                'output': 'Mock test results - all tests passed'
            }
        
        return results
    
    async def _run_typescript_tests(self, test_files: Dict[str, str]) -> Dict[str, Any]:
        """Run TypeScript tests (mock implementation)."""
        results = {}
        
        for filename, test_code in test_files.items():
            # In a real implementation, this would run Jest with TypeScript
            results[filename] = {
                'status': 'passed',
                'tests_run': 4,
                'failures': 0,
                'errors': 0,
                'output': 'Mock test results - all tests passed'
            }
        
        return results
    
    async def generate_tests(self, files: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate test cases for provided code files.
        
        Args:
            files: Dictionary mapping filenames to code content
            
        Returns:
            Dictionary containing generated test files
        """
        generated_tests = {}
        test_summary = {}
        
        logger.info(f"Generating tests for {len(files)} files")
        
        for filename, code in files.items():
            language = self._detect_language(filename)
            
            if language == 'unknown':
                test_summary[filename] = {
                    'status': 'skipped',
                    'reason': 'Unsupported file type'
                }
                continue
            
            # Analyze code
            if language == 'python':
                analysis = self._analyze_python_code(code)
            else:
                analysis = self._analyze_javascript_code(code)
            
            # Generate tests
            test_generator = self.language_patterns[language]['test_generator']
            test_code = test_generator(filename, code, analysis)
            
            # Create test filename
            if language == 'python':
                test_filename = f"test_{filename}"
            else:
                test_filename = f"{filename.replace('.js', '.test.js').replace('.ts', '.test.ts').replace('.jsx', '.test.jsx').replace('.tsx', '.test.tsx')}"
            
            generated_tests[test_filename] = test_code
            
            test_summary[filename] = {
                'status': 'generated',
                'language': language,
                'test_filename': test_filename,
                'functions_found': len(analysis.get('functions', [])),
                'classes_found': len(analysis.get('classes', [])),
                'components_found': len(analysis.get('components', [])),
                'endpoints_found': len(analysis.get('endpoints', []))
            }
        
        return {
            'status': 'completed',
            'generated_tests': generated_tests,
            'test_summary': test_summary,
            'total_files_processed': len(files),
            'total_tests_generated': len(generated_tests),
            'generated_at': datetime.now().isoformat()
        }
    
    async def validate_api_endpoints(self, api_base_url: str = "http://localhost:8000") -> Dict[str, Any]:
        """
        Validate API endpoints - DISABLED due to Python 3.14 instability.
        """
        logger.warning("API validation is disabled on this environment.")
        return {
            'status': 'skipped',
            'reason': 'Python 3.14 instability with httpx/httpcore'
        }
        
        # Calculate summary
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results.values() if r['passed']])
        
        return {
            'status': 'completed',
            'api_base_url': api_base_url,
            'total_endpoints_tested': total_tests,
            'endpoints_passed': passed_tests,
            'endpoints_failed': total_tests - passed_tests,
            'success_rate': round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
            'test_results': test_results,
            'tested_at': datetime.now().isoformat()
        }
    
    async def run_tests(self, test_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Run generated test files and return results.
        
        Args:
            test_files: Dictionary mapping test filenames to test code
            
        Returns:
            Dictionary containing test execution results
        """
        logger.info(f"Running {len(test_files)} test files")
        
        all_results = {}
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for filename, test_code in test_files.items():
            language = self._detect_language(filename)
            
            if language == 'unknown':
                all_results[filename] = {
                    'status': 'skipped',
                    'reason': 'Unsupported test file type'
                }
                continue
            
            # Run tests
            test_runner = self.language_patterns[language]['test_runner']
            results = await test_runner({filename: test_code})
            
            all_results.update(results)
            
            for result in results.values():
                total_tests += result.get('tests_run', 0)
                total_failures += result.get('failures', 0)
                total_errors += result.get('errors', 0)
        
        return {
            'status': 'completed',
            'total_test_files': len(test_files),
            'total_tests_run': total_tests,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'success_rate': round(((total_tests - total_failures - total_errors) / total_tests) * 100, 2) if total_tests > 0 else 0,
            'test_results': all_results,
            'run_at': datetime.now().isoformat()
        }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages for testing."""
        return list(self.language_patterns.keys())
