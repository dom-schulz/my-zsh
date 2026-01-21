import subprocess
import shutil
import sys
from pathlib import Path
from typing import Optional
import typer
try:
    from rich.console import Console
    from rich.theme import Theme
    console = Console(theme=Theme({"success": "green", "error": "red", "warning": "yellow", "info": "blue"}))
except ImportError:
    console = None

def _log(msg: str, style: str = "white"):
    if console:
        console.print(msg, style=style)
    else:
        typer.echo(msg)

def check_uv_installed() -> bool:
    """Checks if uv is installed and available in PATH."""
    return shutil.which("uv") is not None

def venv_exists(repo_path: Path) -> bool:
    """Checks if .venv directory exists in the repo root."""
    return (repo_path / ".venv").is_dir() and (repo_path / ".venv" / "bin" / "python").exists()

def create_venv(repo_path: Path) -> bool:
    """Creates a virtual environment in the repo root using uv."""
    if not check_uv_installed():
        _log("Error: 'uv' is not installed or not in PATH. Please install uv.", style="error")
        return False

    venv_path = repo_path / ".venv"
    try:
        _log(f"Creating venv at {venv_path} using uv...", style="info")
        # uv venv .venv
        subprocess.run(["uv", "venv", str(venv_path)], check=True, capture_output=True)
        _log("Venv created successfully.", style="success")
        return True
    except subprocess.CalledProcessError as e:
        _log(f"Failed to create venv: {e.stderr.decode() if e.stderr else str(e)}", style="error")
        return False
    except Exception as e:
        _log(f"Error creating venv: {e}", style="error")
        return False

def sync_packages(repo_path: Path, requirements_path: str) -> bool:
    """Installs/syncs packages from requirements file using uv."""
    if not check_uv_installed():
        _log("Error: 'uv' is not installed or not in PATH. Please install uv.", style="error")
        return False

    venv_path = repo_path / ".venv"
    req_file = repo_path / requirements_path
    
    if not req_file.exists():
        _log(f"Requirements file not found: {req_file}", style="error")
        return False

    try:
        _log(f"Syncing packages from {requirements_path} using uv...", style="info")
        
        # uv pip install -r requirements.txt --python .venv
        subprocess.run(
            ["uv", "pip", "install", "-r", str(req_file), "--python", str(venv_path)], 
            check=True, 
            capture_output=False
        )
        _log("Packages synced successfully.", style="success")
        return True
    except subprocess.CalledProcessError as e:
        # uv usually prints to stderr/stdout directly if capture_output=False
        _log("Failed to sync packages.", style="error")
        return False
    except Exception as e:
        _log(f"Error syncing packages: {e}", style="error")
        return False
