from typing import Dict, Any, List, Optional, Tuple
import logging
import re
import ast
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class DebugService:
    def __init__(self):
        self.language_patterns = {
            'python': {
                'extensions': ['.py'],
                'syntax_check': self._check_python_syntax,
                'common_fixes': self._fix_python_issues
            },
            'javascript': {
                'extensions': ['.js', '.jsx'],
                'syntax_check': self._check_javascript_syntax,
                'common_fixes': self._fix_javascript_issues
            },
            'typescript': {
                'extensions': ['.ts', '.tsx'],
                'syntax_check': self._check_typescript_syntax,
                'common_fixes': self._fix_typescript_issues
            },
            'json': {
                'extensions': ['.json'],
                'syntax_check': self._check_json_syntax,
                'common_fixes': self._fix_json_issues
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
    
    def _check_python_syntax(self, code: str) -> List[Dict[str, Any]]:
        """Check Python syntax errors."""
        errors = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append({
                'type': 'syntax_error',
                'line': e.lineno or 1,
                'column': e.offset or 1,
                'message': str(e),
                'severity': 'error'
            })
        except Exception as e:
            errors.append({
                'type': 'parse_error',
                'line': 1,
                'column': 1,
                'message': str(e),
                'severity': 'error'
            })
        
        # Check for common Python issues
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for missing imports
            if re.search(r'\b(FastAPI|APIRouter|BaseModel|pydantic|sqlalchemy)\b', line):
                if not any('import' in prev_line for prev_line in lines[:i-1]):
                    errors.append({
                        'type': 'missing_import',
                        'line': i,
                        'column': 1,
                        'message': f'Possible missing import for modules used in line {i}',
                        'severity': 'warning'
                    })
            
            # Check for undefined variables
            if re.search(r'\b(app|router|db)\b', line):
                if not any('app =' in prev_line or 'router =' in prev_line or 'db =' in prev_line for prev_line in lines[:i-1]):
                    errors.append({
                        'type': 'undefined_variable',
                        'line': i,
                        'column': 1,
                        'message': f'Possible undefined variable used in line {i}',
                        'severity': 'warning'
                    })
        
        return errors
    
    def _check_javascript_syntax(self, code: str) -> List[Dict[str, Any]]:
        """Check JavaScript syntax errors."""
        errors = []
        
        # Basic syntax checks
        if code.count('{') != code.count('}'):
            errors.append({
                'type': 'mismatched_braces',
                'line': 1,
                'column': 1,
                'message': 'Mismatched curly braces',
                'severity': 'error'
            })
        
        if code.count('(') != code.count(')'):
            errors.append({
                'type': 'mismatched_parentheses',
                'line': 1,
                'column': 1,
                'message': 'Mismatched parentheses',
                'severity': 'error'
            })
        
        # Check for common React issues
        if 'import React' not in code and ('useState' in code or 'useEffect' in code):
            errors.append({
                'type': 'missing_react_import',
                'line': 1,
                'column': 1,
                'message': 'Missing React import for hooks usage',
                'severity': 'error'
            })
        
        return errors
    
    def _check_typescript_syntax(self, code: str) -> List[Dict[str, Any]]:
        """Check TypeScript syntax errors."""
        errors = []
        
        # Inherit JavaScript checks
        errors.extend(self._check_javascript_syntax(code))
        
        # TypeScript specific checks
        if 'interface' in code and 'export' not in code:
            errors.append({
                'type': 'missing_export',
                'line': 1,
                'column': 1,
                'message': 'Interface might need to be exported',
                'severity': 'warning'
            })
        
        return errors
    
    def _check_json_syntax(self, code: str) -> List[Dict[str, Any]]:
        """Check JSON syntax errors."""
        errors = []
        
        try:
            json.loads(code)
        except json.JSONDecodeError as e:
            errors.append({
                'type': 'json_syntax_error',
                'line': e.lineno or 1,
                'column': e.colno or 1,
                'message': f'JSON syntax error: {str(e)}',
                'severity': 'error'
            })
        
        return errors
    
    def _fix_python_issues(self, code: str, errors: List[Dict[str, Any]]) -> str:
        """Fix common Python issues."""
        lines = code.split('\n')
        fixed_lines = lines.copy()
        
        # Add missing imports
        imports_to_add = []
        
        for error in errors:
            if error['type'] == 'missing_import':
                line_content = fixed_lines[error['line'] - 1]
                
                if 'FastAPI' in line_content and 'from fastapi import FastAPI' not in code:
                    imports_to_add.append('from fastapi import FastAPI')
                
                if 'APIRouter' in line_content and 'from fastapi import APIRouter' not in code:
                    imports_to_add.append('from fastapi import APIRouter')
                
                if 'BaseModel' in line_content and 'from pydantic import BaseModel' not in code:
                    imports_to_add.append('from pydantic import BaseModel')
        
        # Add imports at the beginning
        if imports_to_add:
            import_lines = []
            for imp in imports_to_add:
                if imp not in code:
                    import_lines.append(imp)
            
            if import_lines:
                fixed_lines = import_lines + [''] + fixed_lines
        
        # Fix common syntax issues
        for i, line in enumerate(fixed_lines):
            # Fix missing colons in function definitions
            if re.match(r'^\s*(def|class|if|elif|else|for|while|try|except|finally|with)\s+.*[^\s:]$', line):
                fixed_lines[i] = line + ':'
        
        return '\n'.join(fixed_lines)
    
    def _fix_javascript_issues(self, code: str, errors: List[Dict[str, Any]]) -> str:
        """Fix common JavaScript issues."""
        fixed_code = code
        
        # Add missing React import
        for error in errors:
            if error['type'] == 'missing_react_import':
                if 'import React' not in fixed_code:
                    fixed_code = "import React from 'react';\n" + fixed_code
        
        # Fix basic syntax issues
        # Add missing semicolons (basic heuristic)
        lines = fixed_code.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.endswith((';', '{', '}', '(', ')', ',', '[', ']')):
                if not stripped.startswith(('//', '/*', '*', 'import', 'export', 'function', 'class', 'const', 'let', 'var')):
                    lines[i] = line + ';'
        
        return '\n'.join(lines)
    
    def _fix_typescript_issues(self, code: str, errors: List[Dict[str, Any]]) -> str:
        """Fix common TypeScript issues."""
        fixed_code = self._fix_javascript_issues(code, errors)
        
        # Add type annotations where missing (basic heuristic)
        lines = fixed_code.split('\n')
        for i, line in enumerate(lines):
            # Add type to function parameters
            if 'function(' in line and ':' not in line.split('(')[1].split(')')[0]:
                line = re.sub(r'function\(([^)]+)\)', r'function(\1: any)', line)
                lines[i] = line
        
        return '\n'.join(lines)
    
    def _fix_json_issues(self, code: str, errors: List[Dict[str, Any]]) -> str:
        """Fix common JSON issues."""
        fixed_code = code.strip()
        
        # Try to parse and reformat
        try:
            parsed = json.loads(fixed_code)
            return json.dumps(parsed, indent=2)
        except:
            # Basic fixes
            fixed_code = re.sub(r',\s*}', '}', fixed_code)  # Remove trailing commas
            fixed_code = re.sub(r',\s*]', ']', fixed_code)  # Remove trailing commas in arrays
            
            return fixed_code
    
    async def analyze_code(self, files: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze generated code for errors and issues.
        
        Args:
            files: Dictionary mapping filenames to code content
            
        Returns:
            Dictionary containing analysis results
        """
        analysis_results = {}
        total_errors = 0
        total_warnings = 0
        
        logger.info(f"Analyzing {len(files)} files for errors")
        
        for filename, code in files.items():
            language = self._detect_language(filename)
            
            if language == 'unknown':
                analysis_results[filename] = {
                    'language': 'unknown',
                    'errors': [],
                    'warnings': [],
                    'status': 'skipped',
                    'message': 'Unknown file type'
                }
                continue
            
            # Check syntax
            syntax_check = self.language_patterns[language]['syntax_check']
            errors = syntax_check(code)
            
            # Separate errors and warnings
            file_errors = [e for e in errors if e['severity'] == 'error']
            file_warnings = [e for e in errors if e['severity'] == 'warning']
            
            analysis_results[filename] = {
                'language': language,
                'errors': file_errors,
                'warnings': file_warnings,
                'status': 'has_issues' if file_errors else 'ok',
                'total_issues': len(errors)
            }
            
            total_errors += len(file_errors)
            total_warnings += len(file_warnings)
        
        return {
            'status': 'completed',
            'total_files': len(files),
            'files_with_errors': len([f for f in analysis_results.values() if f['status'] == 'has_issues']),
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'analysis': analysis_results,
            'analyzed_at': datetime.now().isoformat()
        }
    
    async def fix_code(self, files: Dict[str, str], analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Fix detected issues in generated code.
        
        Args:
            files: Dictionary mapping filenames to code content
            analysis: Previous analysis results (optional)
            
        Returns:
            Dictionary containing fixed code and fix summary
        """
        if not analysis:
            analysis = await self.analyze_code(files)
        
        fixed_files = {}
        fix_summary = {}
        total_fixes = 0
        
        logger.info(f"Fixing issues in {len(files)} files")
        
        for filename, code in files.items():
            language = self._detect_language(filename)
            
            if language == 'unknown':
                fixed_files[filename] = code
                fix_summary[filename] = {
                    'status': 'skipped',
                    'fixes_applied': 0,
                    'message': 'Unknown file type'
                }
                continue
            
            file_analysis = analysis['analysis'].get(filename, {})
            errors = file_analysis.get('errors', [])
            
            if not errors:
                fixed_files[filename] = code
                fix_summary[filename] = {
                    'status': 'no_fixes_needed',
                    'fixes_applied': 0
                }
                continue
            
            # Apply fixes
            fix_function = self.language_patterns[language]['common_fixes']
            fixed_code = fix_function(code, errors)
            
            fixed_files[filename] = fixed_code
            
            # Count fixes (basic heuristic)
            fixes_applied = len(errors)
            total_fixes += fixes_applied
            
            fix_summary[filename] = {
                'status': 'fixed',
                'fixes_applied': fixes_applied,
                'original_length': len(code),
                'fixed_length': len(fixed_code)
            }
        
        return {
            'status': 'completed',
            'total_files': len(files),
            'files_fixed': len([f for f in fix_summary.values() if f['status'] == 'fixed']),
            'total_fixes_applied': total_fixes,
            'fixed_files': fixed_files,
            'fix_summary': fix_summary,
            'fixed_at': datetime.now().isoformat()
        }
    
    async def debug_and_fix(self, files: Dict[str, str]) -> Dict[str, Any]:
        """
        Complete debug and fix workflow.
        
        Args:
            files: Dictionary mapping filenames to code content
            
        Returns:
            Dictionary containing analysis and fixed code
        """
        logger.info("Starting complete debug and fix workflow")
        
        # Analyze code
        analysis = await self.analyze_code(files)
        
        # Fix issues
        fix_result = await self.fix_code(files, analysis)
        
        return {
            'analysis': analysis,
            'fix_result': fix_result,
            'workflow_status': 'completed',
            'processed_at': datetime.now().isoformat()
        }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages."""
        return list(self.language_patterns.keys())
