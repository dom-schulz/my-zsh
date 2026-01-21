import subprocess
import typer
from pathlib import Path
from typing import List, Optional

def run_docker_compose(repo_path: Path, args: List[str], check: bool = False, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Run a docker compose command in the given repository."""
    try:
        # Check if docker-compose.yml exists
        if not (repo_path / "docker-compose.yml").exists() and not (repo_path / "docker-compose.yaml").exists():
             typer.echo(f"Error: No docker-compose.yml found in {repo_path}", err=True)
             raise typer.Exit(code=1)

        cmd = ["docker", "compose"] + args
        
        return subprocess.run(
            cmd,
            cwd=repo_path,
            check=check,
            capture_output=capture_output,
            text=True
        )
    except subprocess.CalledProcessError as e:
        if check:
            raise e
        return e
    except FileNotFoundError:
        typer.echo("Error: 'docker' command not found. Is Docker installed?", err=True)
        raise typer.Exit(code=1)

def print_header(repo_name: str, command: str, color: str = "white"):
    """Print a colored header for the operation."""
    header = f"--- {repo_name} [{command}] ---"
    try:
        from rich.console import Console
        console = Console()
        console.print(header, style=color)
    except ImportError:
        typer.secho(header, fg=color if not color.startswith("#") else None)

def up(repo_path: Path, repo_name: str, color: str, detached: bool = False, build: bool = False):
    """Run docker compose up."""
    args = ["up"]
    if detached:
        args.append("-d")
    if build:
        args.append("--build")
    
    cmd_display = "up"
    if detached: cmd_display += " -d"
    if build: cmd_display += " --build"
    
    print_header(repo_name, cmd_display, color)
    run_docker_compose(repo_path, args)

def down(repo_path: Path, repo_name: str, color: str, volumes: bool = False):
    """Run docker compose down."""
    args = ["down"]
    if volumes:
        args.append("-v")
    
    cmd_display = "down"
    if volumes: cmd_display += " -v"
    
    print_header(repo_name, cmd_display, color)
    run_docker_compose(repo_path, args)

def build(repo_path: Path, repo_name: str, color: str):
    """Run docker compose build."""
    print_header(repo_name, "build", color)
    run_docker_compose(repo_path, ["build"])
