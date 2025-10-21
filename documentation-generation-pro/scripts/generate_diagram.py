#!/usr/bin/env python3
"""
Architecture Diagram Generator

Analyzes codebase structure and generates Mermaid diagrams
for architecture, data flow, and database schemas.

Usage:
    python generate_diagram.py --type architecture --output docs/diagrams/
    python generate_diagram.py --type flow --source-file app.py
    python generate_diagram.py --type database --schema-file models.py
"""

import argparse
import ast
from pathlib import Path


class ArchitectureDiagramGenerator:
    """Generate system architecture diagrams"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.components = {}
        self.relationships = []

    def analyze_project(self):
        """Analyze project structure to identify components"""
        # Look for common architectural patterns
        self._find_api_layer()
        self._find_database_layer()
        self._find_services()
        self._find_frontend()

    def _find_api_layer(self):
        """Identify API/controller layer"""
        api_files = list(self.project_path.glob("**/api/**/*.py"))
        api_files.extend(list(self.project_path.glob("**/routes/**/*.py")))
        api_files.extend(list(self.project_path.glob("**/controllers/**/*.py")))

        if api_files:
            self.components["API Layer"] = {
                "type": "api",
                "files": api_files
            }

    def _find_database_layer(self):
        """Identify database layer"""
        db_files = list(self.project_path.glob("**/models/**/*.py"))
        db_files.extend(list(self.project_path.glob("**/database/**/*.py")))

        if db_files:
            self.components["Database"] = {
                "type": "database",
                "files": db_files
            }

    def _find_services(self):
        """Identify service layer"""
        service_files = list(self.project_path.glob("**/services/**/*.py"))
        service_files.extend(list(self.project_path.glob("**/business/**/*.py")))

        if service_files:
            self.components["Services"] = {
                "type": "service",
                "files": service_files
            }

    def _find_frontend(self):
        """Identify frontend components"""
        frontend_dirs = ["frontend", "client", "public", "src"]
        for dir_name in frontend_dirs:
            frontend_path = self.project_path / dir_name
            if frontend_path.exists():
                self.components["Frontend"] = {
                    "type": "frontend",
                    "path": frontend_path
                }
                break

    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram"""
        lines = ["```mermaid", "graph TB"]

        # Add components
        node_map = {}
        node_id = ord('A')

        for comp_name, comp_info in self.components.items():
            node_label = chr(node_id)
            node_map[comp_name] = node_label

            # Style based on type
            if comp_info["type"] == "database":
                lines.append(f"    {node_label}[({comp_name})]")
            elif comp_info["type"] == "api":
                lines.append(f"    {node_label}[{comp_name}]")
            else:
                lines.append(f"    {node_label}[{comp_name}]")

            node_id += 1

        # Add relationships
        if "Frontend" in node_map and "API Layer" in node_map:
            lines.append(f"    {node_map['Frontend']} -->|HTTP| {node_map['API Layer']}")

        if "API Layer" in node_map and "Services" in node_map:
            lines.append(f"    {node_map['API Layer']} --> {node_map['Services']}")

        if "Services" in node_map and "Database" in node_map:
            lines.append(f"    {node_map['Services']} --> {node_map['Database']}")

        if "API Layer" in node_map and "Database" in node_map and "Services" not in node_map:
            lines.append(f"    {node_map['API Layer']} --> {node_map['Database']}")

        lines.append("```")
        return "\n".join(lines)


class DataFlowDiagramGenerator:
    """Generate data flow diagrams for specific files"""

    def __init__(self, source_file: str):
        self.source_file = Path(source_file)
        self.functions = []
        self.calls = []

    def analyze(self):
        """Analyze source file for function calls"""
        with open(self.source_file, 'r') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.functions.append(node.name)
                    # Find function calls within this function
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                self.calls.append((node.name, child.func.id))
        except SyntaxError:
            pass

    def generate_mermaid(self) -> str:
        """Generate Mermaid flowchart"""
        lines = ["```mermaid", "flowchart TD"]

        # Add nodes for each function
        for i, func in enumerate(self.functions):
            lines.append(f"    {chr(65 + i)}[{func}]")

        # Add edges for function calls
        func_to_node = {func: chr(65 + i) for i, func in enumerate(self.functions)}

        for caller, callee in self.calls:
            if caller in func_to_node and callee in func_to_node:
                lines.append(f"    {func_to_node[caller]} --> {func_to_node[callee]}")

        lines.append("```")
        return "\n".join(lines)


class DatabaseDiagramGenerator:
    """Generate database schema diagrams"""

    def __init__(self, schema_file: str):
        self.schema_file = Path(schema_file)
        self.tables = []

    def analyze(self):
        """Analyze schema file for models/tables"""
        with open(self.schema_file, 'r') as f:
            content = f.read()

        # Look for class definitions (SQLAlchemy, Django ORM)
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it inherits from Base or Model
                    if node.bases:
                        table_info = {
                            "name": node.name,
                            "fields": []
                        }

                        # Extract fields
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign):
                                if isinstance(item.target, ast.Name):
                                    table_info["fields"].append(item.target.id)
                            elif isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        table_info["fields"].append(target.id)

                        if table_info["fields"]:
                            self.tables.append(table_info)
        except SyntaxError:
            pass

    def generate_mermaid(self) -> str:
        """Generate Mermaid ER diagram"""
        lines = ["```mermaid", "erDiagram"]

        for table in self.tables:
            table_name = table["name"]
            lines.append(f"    {table_name} {{")
            for field in table["fields"][:10]:  # Limit to 10 fields
                lines.append(f"        string {field}")
            lines.append("    }")

        lines.append("```")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate architecture diagrams")
    parser.add_argument("--type", choices=["architecture", "flow", "database"],
                        required=True, help="Diagram type")
    parser.add_argument("--path", default=".", help="Project path (for architecture)")
    parser.add_argument("--source-file", help="Source file (for flow)")
    parser.add_argument("--schema-file", help="Schema file (for database)")
    parser.add_argument("--output", default="docs/diagrams", help="Output directory")

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate diagram based on type
    if args.type == "architecture":
        generator = ArchitectureDiagramGenerator(args.path)
        generator.analyze_project()
        diagram = generator.generate_mermaid()
        output_file = output_dir / "architecture.md"

        # Create a complete markdown file
        content = f"""# System Architecture

{diagram}

## Components

"""
        for comp_name, comp_info in generator.components.items():
            content += f"### {comp_name}\n"
            content += f"Type: {comp_info['type']}\n\n"

        output_file.write_text(content)

    elif args.type == "flow":
        if not args.source_file:
            print("Error: --source-file required for flow diagrams")
            return

        generator = DataFlowDiagramGenerator(args.source_file)
        generator.analyze()
        diagram = generator.generate_mermaid()
        output_file = output_dir / "data_flow.md"

        content = f"""# Data Flow

{diagram}

## Functions

"""
        for func in generator.functions:
            content += f"- `{func}`\n"

        output_file.write_text(content)

    else:  # database
        if not args.schema_file:
            print("Error: --schema-file required for database diagrams")
            return

        generator = DatabaseDiagramGenerator(args.schema_file)
        generator.analyze()
        diagram = generator.generate_mermaid()
        output_file = output_dir / "database_schema.md"

        content = f"""# Database Schema

{diagram}

## Tables

"""
        for table in generator.tables:
            content += f"### {table['name']}\n"
            for field in table['fields']:
                content += f"- {field}\n"
            content += "\n"

        output_file.write_text(content)

    print(f"✅ Diagram generated: {output_file}")


if __name__ == "__main__":
    main()
