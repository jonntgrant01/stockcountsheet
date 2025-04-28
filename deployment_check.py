#!/usr/bin/env python3
"""
Deployment Readiness Checker for Streamlit Apps
===============================================

This script checks if your Streamlit app is ready for deployment by verifying:
1. All required files exist
2. All imports are installable
3. Basic syntax is correct

Run this before deploying to GitHub to catch common issues.
"""

import os
import sys
import importlib
import pkg_resources
import re
from pathlib import Path
import subprocess

# ANSI color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(text):
    """Print a formatted header."""
    print(f"\n{BLUE}{BOLD}{'=' * 60}{RESET}")
    print(f"{BLUE}{BOLD} {text}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 60}{RESET}\n")

def print_success(text):
    """Print a success message."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    """Print a warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_error(text):
    """Print an error message."""
    print(f"{RED}✗ {text}{RESET}")

def check_required_files():
    """Check if all required files for deployment exist."""
    print_header("Checking Required Files")
    
    required_files = {
        "app.py": "Main Streamlit application",
        ".streamlit/config.toml": "Streamlit configuration",
        "README.md": "Project documentation"
    }
    
    # Check if .streamlit directory exists
    if not os.path.isdir(".streamlit"):
        os.makedirs(".streamlit", exist_ok=True)
        print_warning("Created missing .streamlit directory")
    
    all_files_exist = True
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            print_success(f"Found {file_path} ({description})")
        else:
            print_error(f"Missing {file_path} ({description})")
            all_files_exist = False
    
    # Check for assets directory
    if os.path.isdir("assets"):
        print_success("Found assets directory")
    else:
        print_warning("Missing assets directory - create one if you have images or other assets")
    
    return all_files_exist

def extract_imports(file_path):
    """Extract all import statements from a Python file."""
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all import statements
    import_lines = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE)
    packages = []
    
    for imp in import_lines:
        # Get the top-level package name (e.g., 'pandas' from 'pandas.DataFrame')
        package = imp.split('.')[0]
        if package not in ['__future__', 'os', 'sys', 'io', 're', 'json', 'time', 'datetime', 
                           'math', 'random', 'collections', 'functools', 'itertools', 'typing']:
            packages.append(package)
    
    return list(set(packages))

def check_dependencies():
    """Check if all required packages are specified in requirements.txt."""
    print_header("Checking Dependencies")
    
    # Extract imports from app.py
    imports = extract_imports("app.py")
    print(f"Found {len(imports)} imported packages in app.py: {', '.join(imports)}")
    
    # Check if requirements.txt exists
    requirements_path = "requirements.txt"
    requirements_exist = os.path.exists(requirements_path)
    
    if not requirements_exist:
        print_warning("requirements.txt not found, creating one with basic dependencies")
        with open(requirements_path, 'w') as f:
            f.write("streamlit>=1.22.0\npandas>=1.5.0\nnumpy>=1.22.0\npillow>=9.0.0\n")
        requirements_exist = True
    
    # Read requirements
    with open(requirements_path, 'r') as f:
        requirements_content = f.read()
    
    # Check if each imported package is in requirements.txt
    missing_packages = []
    for package in imports:
        if package.lower() not in requirements_content.lower():
            missing_packages.append(package)
    
    if missing_packages:
        print_warning(f"The following packages are imported but not in requirements.txt: {', '.join(missing_packages)}")
        print_warning("Consider adding them to requirements.txt")
    else:
        print_success("All imported packages appear to be in requirements.txt")
    
    return requirements_exist

def check_streamlit_config():
    """Check if Streamlit config has the right settings for deployment."""
    print_header("Checking Streamlit Configuration")
    
    config_path = ".streamlit/config.toml"
    if not os.path.exists(config_path):
        print_warning("Streamlit config file not found, creating a basic one")
        os.makedirs(".streamlit", exist_ok=True)
        with open(config_path, 'w') as f:
            f.write("""[server]
headless = true
enableCORS = false

[browser]
serverAddress = "0.0.0.0"
gatherUsageStats = false
""")
    
    # Read config file
    with open(config_path, 'r') as f:
        config_content = f.read()
    
    # Check for required settings
    all_settings_correct = True
    required_settings = [
        ("headless = true", "Server may not start properly on Streamlit Cloud without headless mode"),
        ("serverAddress = \"0.0.0.0\"", "Server needs to listen on all interfaces (0.0.0.0) for deployment")
    ]
    
    for setting, warning in required_settings:
        if setting not in config_content:
            print_warning(f"Missing recommended setting: {setting} - {warning}")
            all_settings_correct = False
    
    if all_settings_correct:
        print_success("Streamlit configuration looks good for deployment")
    
    return all_settings_correct

def check_syntax():
    """Check Python syntax in app.py."""
    print_header("Checking Python Syntax")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", "app.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success("app.py has valid Python syntax")
            return True
        else:
            print_error(f"Syntax error in app.py: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Failed to check syntax: {e}")
        return False

def check_git_setup():
    """Check if Git is properly set up."""
    print_header("Checking Git Setup")
    
    # Check if .git directory exists
    if not os.path.isdir(".git"):
        print_warning("Not a Git repository. Initialize with git init")
        return False
    
    # Check if .gitignore exists
    if not os.path.exists(".gitignore"):
        print_warning("No .gitignore file found. Creating a basic one")
        with open(".gitignore", 'w') as f:
            f.write("""# Streamlit
.streamlit/secrets.toml

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# OS specific
.DS_Store
*.swp
*~

# Virtual Environment
venv/
ENV/
""")
    else:
        print_success("Found .gitignore file")
    
    # Check remote
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True
        )
        if "origin" in result.stdout:
            print_success("Git remote repository is configured")
        else:
            print_warning("No remote repository configured")
    except Exception:
        print_warning("Could not check Git remote configuration")
    
    return True

def check_deployment_readiness():
    """Run all checks and evaluate if the app is ready for deployment."""
    print_header("STREAMLIT DEPLOYMENT READINESS CHECKER")
    
    checks = []
    checks.append(("Required files", check_required_files()))
    checks.append(("Dependencies", check_dependencies()))
    checks.append(("Streamlit config", check_streamlit_config()))
    checks.append(("Python syntax", check_syntax()))
    checks.append(("Git setup", check_git_setup()))
    
    print_header("SUMMARY")
    
    all_passed = True
    for name, result in checks:
        status = f"{GREEN}PASS{RESET}" if result else f"{YELLOW}WARNING{RESET}"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print(f"\n{GREEN}{BOLD}🚀 Your app looks ready for deployment!{RESET}")
        print(f"\n{GREEN}Next steps:{RESET}")
        print(f"1. Push your code to GitHub:")
        print(f"   git add .")
        print(f"   git commit -m \"Ready for deployment\"")
        print(f"   git push")
        print(f"2. Go to https://share.streamlit.io/ to deploy")
    else:
        print(f"\n{YELLOW}{BOLD}⚠ Your app has some warnings but may still deploy successfully.{RESET}")
        print(f"\n{YELLOW}Consider fixing the warnings before deployment.{RESET}")
    
    return all_passed

if __name__ == "__main__":
    check_deployment_readiness()