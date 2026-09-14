"""
Post-generation script for Cookiecutter project.
Sets up the project with selected package manager and initializes Git repository.
"""
import os
import re
import shutil
import subprocess
import sys
from typing import List

# Console colors for better readability
class Colors:
    SUCCESS = '\033[92m'
    INFO = '\033[94m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    RESET = "\x1b[0m"

# Project configuration from cookiecutter
PACKAGE_MANAGER = "{{cookiecutter.package_manager}}"
PROJECT_NAME = "{{cookiecutter.project_name}}"
PROJECT_SLUG = "{{cookiecutter.project_slug}}"
PROJECT_DESCRIPTION = "{{cookiecutter.project_description}}"
PROJECT_AUTHOR = "{{cookiecutter.project_author}}"
RAW_PYTHON_VERSION = "{{cookiecutter.python_version}}"

MINIMUM_PYTHON = (3, 8)

def print_status(message: str, color: str = Colors.INFO) -> None:
    """Print a formatted status message."""
    print(f"{color}{message}{Colors.RESET}")

def get_python_version() -> str:
    """
    Resolves 'latest available' directly from system runtime (sys.version_info).
    Enforces a minimum version of 3.8.
    """
    raw_version = RAW_PYTHON_VERSION.strip().lower()

    if raw_version == "latest available":
        current_version = sys.version_info[:2]
        if current_version < MINIMUM_PYTHON:
            print_status(
                f"Warning: Detected Python {current_version[0]}.{current_version[1]} is lower than minimum (3.8). "
                f"Falling back to 3.8.",
                Colors.WARNING
            )
            return "3.8"
        return f"{current_version[0]}.{current_version[1]}"

    return raw_version

PYTHON_VERSION = get_python_version()

def update_pyproject_file() -> None:
    """Updates pyproject.toml with the resolved target Python version."""
    pyproject_path = "pyproject.toml"
    if not os.path.exists(pyproject_path):
        return

    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()

    if PACKAGE_MANAGER == "poetry":
        content = re.sub(
            r'python\s*=\s*"[^"]+"',
            f'python = "^{PYTHON_VERSION}"',
            content
        )
    elif PACKAGE_MANAGER == "uv":
        content = re.sub(
            r'requires-python\s*=\s*"[^"]+"',
            f'requires-python = ">={PYTHON_VERSION}"',
            content
        )

    with open(pyproject_path, "w", encoding="utf-8") as f:
        f.write(content)

def run_command(command: List[str], error_message: str = "Command failed") -> bool:
    """Run a shell command safely."""
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        print_status(f"Error: {error_message}", Colors.ERROR)
        return False
    
def ensure_tool_installed(tool_name: str) -> bool:
    """Ensure a CLI tool (uv or poetry) is available, attempting installation if missing."""
    if shutil.which(tool_name):
        return True

    print_status(f"'{tool_name}' not found. Attempting installation...", Colors.WARNING)

    # Try pipx first if available
    if shutil.which("pipx"):
        if run_command(["pipx", "install", tool_name], f"Failed to install {tool_name} via pipx"):
            return True

    # Fallback to python -m pip
    print_status(f"Installing {tool_name} via pip...", Colors.INFO)
    if run_command([sys.executable, "-m", "pip", "install", tool_name], f"Failed to install {tool_name} via pip"):
        return True

    return False

def setup_poetry() -> bool:
    """Set up the project using Poetry."""
    if not ensure_tool_installed("poetry"):
        return False
    
    print_status(f"Creating virtual environment with Poetry (Python {PYTHON_VERSION})...", Colors.INFO)
    if not run_command(["poetry", "env", "use", f"python{PYTHON_VERSION}"], 
                       "Failed to set Python version"):
        return False
    
    if not run_command(["poetry", "install"], "Failed to install dependencies"):
        return False
    
    return True

def setup_uv() -> bool:
    """Set up the project using uv."""
    if not ensure_tool_installed("uv"):
        return False
    
    print_status(f"Creating virtual environment with uv (Python {PYTHON_VERSION})...", Colors.INFO)
    if not run_command(["uv", "venv", "--python", f"{PYTHON_VERSION}"], 
                       "Failed to create virtual environment"):
        return False
    
    if not run_command(["uv", "pip", "sync", "pyproject.toml"], 
                       "Failed to install dependencies"):
        return False
    
    return True

def setup_git() -> bool:
    """Initialize git repository with initial commit."""
    print_status("Initializing git repository...", Colors.INFO)
    commands = [
        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Initial commit"],
        ["git", "branch", "-M", "main"]
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Failed to run {' '.join(cmd)}"):
            return False
    
    return True

def main() -> int:
    """Main function that orchestrates the post-generation setup."""
    print_status(f"Setting up project {PROJECT_NAME} with {PACKAGE_MANAGER} (Python {PYTHON_VERSION})...", Colors.SUCCESS)
    
    # Sync pyproject.toml with target version before running package managers
    update_pyproject_file()

    success = False
    if PACKAGE_MANAGER == "poetry":
        success = setup_poetry()
    elif PACKAGE_MANAGER == "uv":
        success = setup_uv()
    else:
        print_status(f"Unsupported package manager: {PACKAGE_MANAGER}", Colors.ERROR)
        return 1
    
    if not success:
        print_status("Failed to set up package manager", Colors.ERROR)
        return 1
    
    if not setup_git():
        print_status("Failed to initialize git repository", Colors.ERROR)
        return 1
    
    print_status(f"Your template for {PROJECT_NAME} is ready!", Colors.SUCCESS)
    return 0

if __name__ == "__main__":
    sys.exit(main())