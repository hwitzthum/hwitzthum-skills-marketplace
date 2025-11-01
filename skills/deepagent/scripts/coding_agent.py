"""
Coding Agent Example - DeepAgents Framework

This script demonstrates building a coding agent with:
- Code execution capability
- File management for organizing code
- Planning for structured implementation
- Testing and validation workflows
"""

import os
import subprocess
import tempfile
from pathlib import Path
from deepagents import create_deep_agent
from langchain_core.tools import tool


@tool
def run_python_code(code: str) -> str:
    """
    Execute Python code in a safe subprocess and return the output.
    
    Args:
        code: Python code to execute
    
    Returns:
        String containing stdout/stderr from execution
    """
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Run the code
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Clean up
        os.unlink(temp_file)
        
        # Return combined output
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
        
        return output or "Code executed successfully with no output"
        
    except subprocess.TimeoutExpired:
        os.unlink(temp_file)
        return "Error: Code execution timed out (10 second limit)"
    except Exception as e:
        return f"Error executing code: {str(e)}"


@tool
def run_tests(test_code: str) -> str:
    """
    Run Python unit tests using pytest.
    
    Args:
        test_code: Python test code (should include pytest tests)
    
    Returns:
        String containing test results
    """
    try:
        # Create a temporary file for the test code
        with tempfile.NamedTemporaryFile(mode='w', suffix='_test.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        # Run pytest
        result = subprocess.run(
            ['python', '-m', 'pytest', temp_file, '-v'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Clean up
        os.unlink(temp_file)
        
        # Return combined output
        output = result.stdout
        if result.stderr:
            output += f"\n\nErrors:\n{result.stderr}"
        
        return output or "Tests completed"
        
    except subprocess.TimeoutExpired:
        os.unlink(temp_file)
        return "Error: Test execution timed out (10 second limit)"
    except Exception as e:
        return f"Error running tests: {str(e)}"


@tool
def lint_code(code: str) -> str:
    """
    Check Python code for style and potential issues using pylint.
    
    Args:
        code: Python code to lint
    
    Returns:
        String containing lint results
    """
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Run pylint
        result = subprocess.run(
            ['python', '-m', 'pylint', temp_file, '--errors-only'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Clean up
        os.unlink(temp_file)
        
        if result.stdout:
            return result.stdout
        return "No issues found"
        
    except subprocess.TimeoutExpired:
        os.unlink(temp_file)
        return "Error: Linting timed out (10 second limit)"
    except Exception as e:
        return f"Error linting code: {str(e)}"


# Main coding agent instructions
coding_agent_instructions = """You are an expert software engineer.

Your workflow for coding tasks:

1. **Plan the implementation** (use write_todos):
   - Break down the requirements into tasks
   - Identify functions/classes needed
   - Plan the structure of the code
   
2. **Write initial code** (use write_file):
   - Implement the core functionality
   - Save code to appropriately named files
   - Follow Python best practices
   
3. **Test the code** (use run_python_code):
   - Execute the code to verify it works
   - Check for runtime errors
   - Verify the output is correct
   
4. **Write tests** (use write_file):
   - Create unit tests in a separate test file
   - Test edge cases and normal operation
   
5. **Run tests** (use run_tests):
   - Execute the test suite
   - Verify all tests pass
   
6. **Lint and fix** (use lint_code and edit_file):
   - Check for code quality issues
   - Fix any problems found
   - Refine the code
   
7. **Document** (use write_file):
   - Create a README explaining the code
   - Include usage examples
   - Document any requirements
   
8. **Organize for delivery**:
   - Use ls to verify all files are created
   - Use read_file to review final versions
   - Present the complete solution to the user

File organization guidelines:
- Main code: `main.py` or `<module_name>.py`
- Tests: `test_<module_name>.py`
- Documentation: `README.md`
- Utilities: `utils.py` (if needed)

Use /memories/ prefix for project context that should persist across sessions:
- write_file /memories/project_context.md for project-level notes
- write_file /memories/design_decisions.md for architectural choices

Always validate your code by actually running it before declaring it complete.
Fix any issues discovered during testing.
"""


def create_coding_agent():
    """
    Create and return a configured deep coding agent.
    
    Returns:
        LangGraph agent configured for coding tasks
    """
    agent = create_deep_agent(
        tools=[run_python_code, run_tests, lint_code],
        system_prompt=coding_agent_instructions,
        model="claude-sonnet-4-20250514",
    )
    return agent


# Example usage
if __name__ == "__main__":
    # Create the agent
    agent = create_coding_agent()
    
    # Example coding task
    coding_task = """Create a Python function that calculates the Fibonacci sequence
    up to n terms. Include error handling, write unit tests, and document the code."""
    
    # Invoke the agent
    print("Starting coding task:", coding_task)
    print("-" * 80)
    
    result = agent.invoke({
        "messages": [{"role": "user", "content": coding_task}]
    })
    
    # Print the final response
    final_message = result["messages"][-1]
    print("\nAgent Response:")
    print("=" * 80)
    print(final_message.content)
    
    # Print files created
    if "files" in result and result["files"]:
        print("\n\nFiles created:")
        print("-" * 80)
        for filename, content in result["files"].items():
            print(f"\n{filename}:")
            print("-" * 40)
            print(content[:500] + "..." if len(content) > 500 else content)
