#!/usr/bin/env python3
"""
API Documentation Extractor

Analyzes code to extract API endpoints, functions, and classes,
then generates documentation in markdown or OpenAPI format.

Usage:
    python extract_api.py --language python --format markdown
    python extract_api.py --language javascript --format openapi --output api_docs/
"""

import argparse
import ast
import json
import re
from pathlib import Path
from typing import List, Dict, Any


class PythonAPIExtractor:
    """Extract API information from Python code"""

    def extract_from_file(self, filepath: Path) -> Dict[str, Any]:
        """Extract functions, classes, and docstrings from a Python file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {"error": f"Syntax error in {filepath}"}

        api_elements = {
            "functions": [],
            "classes": [],
            "endpoints": []
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = self._extract_function(node)
                api_elements["functions"].append(func_info)

                # Check for Flask/FastAPI routes
                if self._is_endpoint(node):
                    api_elements["endpoints"].append(self._extract_endpoint(node))

            elif isinstance(node, ast.ClassDef):
                class_info = self._extract_class(node)
                api_elements["classes"].append(class_info)

        return api_elements

    @staticmethod
    def _extract_function(node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract function information"""
        return {
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "args": [arg.arg for arg in node.args.args],
            "line_number": node.lineno
        }

    def _extract_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract class information"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._extract_function(item))

        return {
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "methods": methods,
            "line_number": node.lineno
        }

    @staticmethod
    def _is_endpoint(node: ast.FunctionDef) -> bool:
        """Check if function is an API endpoint"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if hasattr(decorator.func, 'attr'):
                    if decorator.func.attr in ['route', 'get', 'post', 'put', 'delete', 'patch']:
                        return True
        return False

    @staticmethod
    def _extract_endpoint(node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract API endpoint information"""
        method = "GET"
        path = ""

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if hasattr(decorator.func, 'attr'):
                    method = decorator.func.attr.upper()
                if decorator.args:
                    first_arg = decorator.args[0]
                    if isinstance(first_arg, ast.Constant):
                        path = str(first_arg.value)

        return {
            "method": method,
            "path": path,
            "function": node.name,
            "docstring": ast.get_docstring(node)
        }


class JavaScriptAPIExtractor:
    """Extract API information from JavaScript/TypeScript code"""

    def extract_from_file(self, filepath: Path) -> Dict[str, Any]:
        """Extract functions and endpoints from JavaScript file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        api_elements = {
            "functions": self._extract_functions(content),
            "endpoints": self._extract_express_routes(content)
        }

        return api_elements

    @staticmethod
    def _extract_functions(content: str) -> List[Dict[str, Any]]:
        """Extract function declarations"""
        functions = []

        # Match function declarations
        pattern = r'(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(pattern, content):
            functions.append({
                "name": match.group(1),
                "params": [p.strip() for p in match.group(2).split(',') if p.strip()],
                "async": "async" in match.group(0)
            })

        # Match arrow functions
        pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>'
        for match in re.finditer(pattern, content):
            functions.append({
                "name": match.group(1),
                "params": [p.strip() for p in match.group(2).split(',') if p.strip()],
                "async": "async" in match.group(0)
            })

        return functions

    @staticmethod
    def _extract_express_routes(content: str) -> List[Dict[str, Any]]:
        """Extract Express.js routes"""
        endpoints = []

        # Match app.get(), app.post(), etc.
        pattern = r'app\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]'
        for match in re.finditer(pattern, content):
            endpoints.append({
                "method": match.group(1).upper(),
                "path": match.group(2)
            })

        # Match router.get(), router.post(), etc.
        pattern = r'router\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]'
        for match in re.finditer(pattern, content):
            endpoints.append({
                "method": match.group(1).upper(),
                "path": match.group(2)
            })

        return endpoints


class MarkdownGenerator:
    """Generate markdown documentation from extracted API data"""

    def generate(self, api_data: Dict[str, Any], language: str) -> str:
        """Generate markdown documentation"""
        sections = [
            "# API Documentation\n",
            f"*Generated from {language} code*\n"
        ]

        # Functions
        if api_data.get("functions"):
            sections.append("## Functions\n")
            for func in api_data["functions"]:
                sections.append(self._format_function(func))

        # Classes
        if api_data.get("classes"):
            sections.append("## Classes\n")
            for cls in api_data["classes"]:
                sections.append(self._format_class(cls))

        # API Endpoints
        if api_data.get("endpoints"):
            sections.append("## API Endpoints\n")
            for endpoint in api_data["endpoints"]:
                sections.append(self._format_endpoint(endpoint))

        return "\n".join(sections)

    @staticmethod
    def _format_function(func: Dict[str, Any]) -> str:
        """Format function documentation"""
        output = [f"### `{func['name']}`\n"]

        if func.get('docstring'):
            output.append(f"{func['docstring']}\n")

        if func.get('args'):
            output.append("**Parameters:**")
            for arg in func['args']:
                output.append(f"- `{arg}`")
            output.append("")

        return "\n".join(output)

    @staticmethod
    def _format_class(cls: Dict[str, Any]) -> str:
        """Format class documentation"""
        output = [f"### `{cls['name']}`\n"]

        if cls.get('docstring'):
            output.append(f"{cls['docstring']}\n")

        if cls.get('methods'):
            output.append("**Methods:**")
            for method in cls['methods']:
                output.append(f"- `{method['name']}`")
            output.append("")

        return "\n".join(output)

    @staticmethod
    def _format_endpoint(endpoint: Dict[str, Any]) -> str:
        """Format API endpoint documentation"""
        output = [
            f"### `{endpoint['method']} {endpoint['path']}`\n"
        ]

        if endpoint.get('docstring'):
            output.append(f"{endpoint['docstring']}\n")

        output.append("**Example:**")
        output.append(f"```bash")
        output.append(f"curl -X {endpoint['method']} http://localhost:3000{endpoint['path']}")
        output.append(f"```\n")

        return "\n".join(output)


class OpenAPIGenerator:
    """Generate OpenAPI 3.0 specification from extracted API data"""

    @staticmethod
    def generate(api_data: Dict[str, Any]) -> str:
        """Generate OpenAPI specification"""
        spec: Dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {
                "title": "API Documentation",
                "version": "1.0.0",
                "description": "Auto-generated API documentation"
            },
            "paths": {}
        }

        paths: Dict[str, Dict[str, Any]] = spec["paths"]

        for endpoint in api_data.get("endpoints", []):
            path = endpoint["path"]
            method = endpoint["method"].lower()

            if path not in paths:
                paths[path] = {}

            paths[path][method] = {
                "summary": endpoint.get("docstring", ""),
                "responses": {
                    "200": {
                        "description": "Successful response"
                    }
                }
            }

        return json.dumps(spec, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Extract API documentation from code")
    parser.add_argument("--language", choices=["python", "javascript", "typescript", "java"],
                        default="python", help="Programming language")
    parser.add_argument("--format", choices=["markdown", "openapi"],
                        default="markdown", help="Output format")
    parser.add_argument("--path", default=".", help="Path to analyze")
    parser.add_argument("--output", default="api_docs", help="Output directory")

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize extractor
    if args.language == "python":
        extractor = PythonAPIExtractor()
        file_pattern = "**/*.py"
    else:  # javascript/typescript
        extractor = JavaScriptAPIExtractor()
        file_pattern = "**/*.{js,ts}"

    # Extract API information from all files
    all_api_data = {
        "functions": [],
        "classes": [],
        "endpoints": []
    }

    for filepath in Path(args.path).glob(file_pattern):
        if "node_modules" in str(filepath) or "venv" in str(filepath):
            continue

        try:
            data = extractor.extract_from_file(filepath)
            for key in all_api_data:
                if key in data:
                    all_api_data[key].extend(data[key])
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    # Generate documentation
    if args.format == "markdown":
        generator = MarkdownGenerator()
        output = generator.generate(all_api_data, args.language)
        output_file = output_dir / "api_reference.md"
    else:  # openapi
        generator = OpenAPIGenerator()
        output = generator.generate(all_api_data)
        output_file = output_dir / "openapi.json"

    # Write output
    output_file.write_text(output)
    print(f"✅ API documentation generated: {output_file}")
    print(f"   Found {len(all_api_data['functions'])} functions")
    print(f"   Found {len(all_api_data.get('classes', []))} classes")
    print(f"   Found {len(all_api_data['endpoints'])} endpoints")


if __name__ == "__main__":
    main()
