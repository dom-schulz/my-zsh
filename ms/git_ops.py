import subprocess
import typer
from pathlib import Path
from typing import List, Optional, Tuple

def print_repo_header(repo_name: str, color: str = "white"):
    """Print a colored repository header."""
    header = f"--- {repo_name} ---"
    try:
        from rich.console import Console
        console = Console()
        console.print(header, style=color)
    except ImportError:
        typer.secho(header, fg=color if not color.startswith("#") else None)

def run_git(repo_path: Path, args: List[str], check: bool = False, capture_output: bool = True, disable_pager: bool = False) -> subprocess.CompletedProcess:
    """Run a git command in the given repository."""
    env = None
    if disable_pager:
        import os
        env = os.environ.copy()
        env['GIT_PAGER'] = 'cat'
    
    try:
        return subprocess.run(
            ["git"] + args,
            cwd=repo_path,
            check=check,
            capture_output=capture_output,
            text=True,
            env=env
        )
    except subprocess.CalledProcessError as e:
        if check:
            raise e
        return e

def get_current_branch(repo_path: Path) -> str:
    res = run_git(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
    if res.returncode == 0:
        return res.stdout.strip()
    return "unknown"

def print_status(repo_name: str, repo_path: Path, color: str):
    """Run git status -sb and print with header."""
    branch = get_current_branch(repo_path)
    # Escape brackets for Rich (it treats [...] as style tags)
    header = f"--- \\[{branch}] {repo_name} ---"
    
    try:
        from rich.console import Console
        console = Console()
        console.print(header, style=color)
    except ImportError:
        typer.secho(header, fg=color if not color.startswith("#") else None)

    # To reduce busyness, we will suppress the first line (branch info) since it's in the header.
    res = run_git(repo_path, ["status", "-sb"], capture_output=True)
    if res.returncode != 0:
        typer.echo(f"Error checking status for {repo_name}")
        return

    lines = res.stdout.splitlines()
    if not lines:
        return
        
    # If there is ahead/behind info, we might want to preserve it.
    first_line = lines[0]
    
    # Check for ahead/behind info
    extra_info = ""
    if "[" in first_line and "]" in first_line:
        # Extract content in brackets, e.g. [ahead 1]
        import re
        match = re.search(r"\[(.*?)\]", first_line)
        if match:
            extra_info = f" [{match.group(1)}]"
    
    # print the extra info if it exists, otherwise skip the line.
    if extra_info:
        typer.secho(f"  {extra_info.strip()}", fg="yellow")
    
    # Print remaining lines (status changes)
    for line in lines[1:]:
        typer.echo(line)

def fetch_origin(repo_path: Path, repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    res = run_git(repo_path, ["fetch", "origin"], capture_output=False)
    if res.returncode != 0:
        typer.echo("Git fetch failed", err=True)

def checkout(repo_path: Path, branch: str, repo_name: str = "", color: str = "white") -> bool:
    if repo_name:
        print_repo_header(repo_name, color)
    
    res = run_git(repo_path, ["checkout", branch], capture_output=True)
    if res.returncode == 0:
        typer.echo(f"Switched to branch '{branch}'")
        return True
    else:
        typer.echo(f"Failed to checkout '{branch}': {res.stderr.strip()}", err=True)
        return False

def pull(repo_path: Path, repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    res = run_git(repo_path, ["pull"], capture_output=False)
    if res.returncode != 0:
        typer.echo("Git pull failed", err=True)

def create_branch(repo_path: Path, branch: str, push: bool = False, repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    res = run_git(repo_path, ["checkout", "-b", branch], capture_output=True)
    if res.returncode == 0:
        typer.echo(f"Created and switched to branch '{branch}'")
        if push:
            push_res = run_git(repo_path, ["push", "-u", "origin", branch], capture_output=False)
            if push_res.returncode != 0:
                 typer.echo("Failed to push upstream", err=True)
    else:
        typer.echo(f"Failed to create branch '{branch}': {res.stderr.strip()}", err=True)

def branch_all(repo_path: Path, repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    run_git(repo_path, ["branch", "-a"], capture_output=False, disable_pager=True)

def add_all(repo_path: Path, repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    res = run_git(repo_path, ["add", "."], capture_output=True)
    if res.returncode != 0:
        typer.echo(f"Git add failed: {res.stderr.strip()}", err=True)

def commit(repo_path: Path, message: str, repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    res = run_git(repo_path, ["commit", "-m", message], capture_output=False)
    if res.returncode != 0:
        typer.echo("Git commit failed", err=True)

def push(repo_path: Path, force: bool = False, default_branch: str = "main", repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    current = get_current_branch(repo_path)
    if force and current == default_branch:
        typer.echo(f"Error: Cannot force push to default branch '{default_branch}'", err=True)
        return

    args = ["push", "origin"]
    if force:
        args.append("--force")
    
    # Try standard push first
    res = run_git(repo_path, args, capture_output=True)
    if res.returncode == 0:
        typer.echo(res.stdout)
    else:
        if "has no upstream branch" in res.stderr:
             typer.echo("No upstream branch. Pushing and setting upstream...")
             args.append("-u")
             # Re-add branch name to be explicit or let git handle HEAD
             # explicit: git push -u origin <current>
             args.append(current)
             res2 = run_git(repo_path, args, capture_output=False)
             if res2.returncode != 0:
                 typer.echo("Push failed", err=True)
        else:
            typer.echo(f"Push failed: {res.stderr.strip()}", err=True)

def fetch_prune_delete(repo_path: Path, force: bool, repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    if not force:
        typer.echo("Operation requires --force")
        return

    typer.echo("Fetching and pruning...")
    run_git(repo_path, ["fetch", "--prune"])
    
    # Find gone branches
    # %(upstream:track) prints "[gone]" for branches whose upstream is removed
    res = run_git(repo_path, ["for-each-ref", "--format=%(refname:short) %(upstream:track)", "refs/heads"])
    if res.returncode != 0:
        typer.echo("Failed to list branches", err=True)
        return

    gone_branches = []
    for line in res.stdout.splitlines():
        if "[gone]" in line:
            parts = line.split()
            if parts:
                gone_branches.append(parts[0])

    if not gone_branches:
        typer.echo("No local branches to prune.")
        return

    for branch in gone_branches:
        if branch == get_current_branch(repo_path):
            typer.echo(f"Skipping deletion of current branch '{branch}' (even though upstream is gone).")
            continue
            
        typer.echo(f"Deleting branch '{branch}'...")
        del_res = run_git(repo_path, ["branch", "-D", branch], capture_output=True)
        if del_res.returncode == 0:
            typer.echo(f"Deleted {branch}")
        else:
            typer.echo(f"Failed to delete {branch}: {del_res.stderr.strip()}", err=True)

def diff(repo_path: Path, args: List[str], repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    # Use capture_output=False to let git diff use pager/interactive mode
    run_git(repo_path, ["diff"] + args, capture_output=False)
