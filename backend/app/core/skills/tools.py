import os
import subprocess
from pathlib import Path
from duckduckgo_search import DDGS
from langchain_core.tools import tool

# Ensure workspace directory exists
WORKSPACE_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../workspace")))
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

@tool
def web_search(query: str) -> str:
    """
    Search the web for real-time information using DuckDuckGo.
    Use this tool when you need up-to-date facts, news, or general web searches.
    """
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No results found."
        formatted_results = "\n\n".join([f"Title: {r['title']}\nSnippet: {r['body']}\nLink: {r['href']}" for r in results])
        return formatted_results
    except Exception as e:
        return f"Error performing web search: {str(e)}"

@tool
def file_manager(action: str, file_path: str, content: str = "") -> str:
    """
    Read or write files in the restricted /workspace directory.
    - action: Must be either 'read' or 'write'.
    - file_path: The relative path to the file inside the workspace (e.g., 'data.txt').
    - content: The content to write (only required if action is 'write').
    """
    target_path = WORKSPACE_DIR / file_path
    
    # Security check: Prevent path traversal
    if not os.path.normpath(target_path).startswith(os.path.normpath(WORKSPACE_DIR)):
        return "Error: Path traversal detected. You can only access files within the workspace."

    try:
        if action == "read":
            if not target_path.exists():
                return f"Error: File '{file_path}' does not exist."
            with open(target_path, "r", encoding="utf-8") as f:
                return f.read()
                
        elif action == "write":
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to '{file_path}'."
            
        else:
            return "Error: Invalid action. Use 'read' or 'write'."
            
    except Exception as e:
        return f"Error performing file operation: {str(e)}"

@tool
def code_interpreter(code: str) -> str:
    """
    Execute Python code in a local subprocess and return the stdout.
    The code is executed within the /workspace directory context.
    Use this to run calculations, scripts, or data processing.
    """
    try:
        # Write code to a temporary file in the workspace
        temp_file = WORKSPACE_DIR / "temp_exec.py"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code)
            
        # Execute the python script
        result = subprocess.run(
            ["python", str(temp_file)],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
            timeout=10 # 10 seconds timeout to prevent infinite loops
        )
        
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()
            
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
            
        return output.strip() if output else "Execution finished with no output."
        
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out after 10 seconds."
    except Exception as e:
        return f"Error executing code: {str(e)}"
