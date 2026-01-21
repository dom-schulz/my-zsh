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

    # To reduce busyness, suppress the first line (branch info) since it's in the header.
    res = run_git(repo_path, ["status", "-sb"], capture_output=True)
    if res.returncode != 0:
        typer.echo(f"Error checking status for {repo_name}")
        return

    lines = res.stdout.splitlines()
    if not lines:
        return
        
    # If there is ahead/behind info, preserve it.
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
    
    # Add spacing between repos
    typer.echo()

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
    
    # First, run git add
    res = run_git(repo_path, ["add", "."], capture_output=True)
    if res.returncode != 0:
        typer.echo(f"Git add failed: {res.stderr.strip()}", err=True)
        return
    
    # Show what was staged using git diff --cached --name-status
    diff_res = run_git(repo_path, ["diff", "--cached", "--name-status"], capture_output=True)
    if diff_res.returncode == 0 and diff_res.stdout.strip():
        typer.echo("Staged files:")
        for line in diff_res.stdout.strip().split('\n'):
            if line:
                typer.echo(f"  {line}")
    else:
        typer.echo("No changes to stage.")

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

    # Check if branch has upstream
    upstream_check = run_git(repo_path, ["rev-parse", "--abbrev-ref", f"{current}@{{upstream}}"], capture_output=True)
    
    args = ["push", "origin"]
    if force:
        args.append("--force")
    
    # If no upstream, set it
    if upstream_check.returncode != 0:
        typer.echo("No upstream branch. Pushing and setting upstream...")
        args.append("-u")
        args.append(current)
    
    # Push with output shown
    res = run_git(repo_path, args, capture_output=False)
    if res.returncode != 0:
        typer.echo("Push failed", err=True)

def get_commits_ahead(repo_path: Path, branch: str, base_branch: str) -> int:
    """Get number of commits current branch is ahead of base branch."""
    res = run_git(
        repo_path, 
        ["rev-list", "--count", f"origin/{base_branch}..{branch}"],
        capture_output=True
    )
    if res.returncode == 0 and res.stdout.strip():
        return int(res.stdout.strip())
    return 0

def create_pull_request(
    repo_path: Path, 
    branch: str, 
    base_branch: str,
    title: str,
    draft: bool = False,
    repo_name: str = "",
    color: str = "white"
) -> bool:
    """Create a pull request using GitHub CLI."""
    if repo_name:
        print_repo_header(repo_name, color)
    
    # Check if gh CLI is available
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        typer.echo("Error: GitHub CLI (gh) is not installed or not in PATH.", err=True)
        typer.echo("Install it: https://cli.github.com/", err=True)
        return False
    
    # Build gh pr create command
    cmd = ["gh", "pr", "create", "--base", base_branch, "--head", branch, "--title", title, "--fill"]
    if draft:
        cmd.append("--draft")
    
    # Run gh command
    res = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    
    if res.returncode == 0:
        # Extract PR URL from output
        pr_url = res.stdout.strip().split('\n')[-1]
        typer.echo(f"✓ Created PR: {pr_url}")
        return True
    else:
        if "already exists" in res.stderr.lower():
            typer.echo("  PR already exists")
            return False
        else:
            typer.echo(f"  Failed: {res.stderr.strip()}", err=True)
            return False

def fetch_prune_delete(repo_path: Path, force: bool, repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    if not force:
        typer.echo("Operation requires --force")
        return

    typer.echo("Fetching and pruning...")
    run_git(repo_path, ["fetch", "--prune"])
    
    # Get all local branches
    local_res = run_git(repo_path, ["for-each-ref", "--format=%(refname:short)", "refs/heads"])
    if local_res.returncode != 0:
        typer.echo("Failed to list local branches", err=True)
        return
    
    local_branches = set(local_res.stdout.strip().split('\n'))
    current = get_current_branch(repo_path)
    
    # Get all remote branches (without origin/ prefix)
    remote_res = run_git(repo_path, ["for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"])
    if remote_res.returncode != 0:
        typer.echo("Failed to list remote branches", err=True)
        return
    
    remote_branches = set()
    for branch in remote_res.stdout.strip().split('\n'):
        if branch and branch.startswith('origin/'):
            # Strip origin/ prefix
            remote_branches.add(branch.replace('origin/', '', 1))
    
    # Find branches that exist locally but not in origin
    branches_to_delete = []
    for branch in local_branches:
        if branch and branch != current and branch not in remote_branches and branch != 'HEAD':
            branches_to_delete.append(branch)
    
    if not branches_to_delete:
        typer.echo("No local branches to prune.")
        return

    typer.echo(f"Found {len(branches_to_delete)} branch(es) not in origin:")
    for branch in branches_to_delete:
        typer.echo(f"  - {branch}")
    
    for branch in branches_to_delete:
        typer.echo(f"Deleting branch '{branch}'...")
        del_res = run_git(repo_path, ["branch", "-D", branch], capture_output=True)
        if del_res.returncode == 0:
            typer.echo(f"  ✓ Deleted {branch}")
        else:
            typer.echo(f"  ✗ Failed to delete {branch}: {del_res.stderr.strip()}", err=True)

def diff(repo_path: Path, args: List[str], repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    # Use capture_output=False to let git diff use pager/interactive mode
    run_git(repo_path, ["diff"] + args, capture_output=False)

def get_github_repo_url(repo_path: Path) -> Optional[str]:
    """Get the GitHub repository URL from git remote."""
    try:
        res = run_git(repo_path, ["remote", "get-url", "origin"], capture_output=True)
        if res.returncode == 0:
            url = res.stdout.strip()
            # Convert SSH to HTTPS format if needed
            # git@github.com:owner/repo.git -> https://github.com/owner/repo
            if url.startswith("git@github.com:"):
                url = url.replace("git@github.com:", "https://github.com/")
            # Remove .git suffix
            if url.endswith(".git"):
                url = url[:-4]
            return url
        return None
    except Exception:
        return None

def list_pull_requests(repo_path: Path, repo_name: str = "", color: str = "white") -> bool:
    """List open pull requests using GitHub CLI."""
    # Check if gh CLI is available
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        typer.echo("Error: GitHub CLI (gh) is not installed or not in PATH.", err=True)
        typer.echo("Install it: https://cli.github.com/", err=True)
        return False
    
    # Run gh pr list command
    cmd = ["gh", "pr", "list", "--json", "number,title,headRefName,state,url", "--limit", "100"]
    res = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    
    if res.returncode != 0:
        if "no pull requests" in res.stderr.lower() or not res.stdout.strip() or res.stdout.strip() == "[]":
            return False
        else:
            typer.echo(f"  Error: {res.stderr.strip()}", err=True)
            return False
    
    # Parse JSON output
    import json
    try:
        prs = json.loads(res.stdout)
        if not prs:
            return False
        
        if repo_name:
            print_repo_header(repo_name, color)
        
        for pr in prs:
            typer.echo(f"  #{pr['number']}: {pr['title']}")
            typer.echo(f"    Branch: {pr['headRefName']}")
            typer.echo()
        
        return True
    except json.JSONDecodeError:
        typer.echo(f"  Error: Failed to parse PR list", err=True)
        return False

def open_pull_request_in_cursor(repo_path: Path, pr_number: int, repo_name: str = "", color: str = "white") -> bool:
    """Open a pull request in Cursor by checking out the PR branch using GitHub CLI."""
    if repo_name:
        print_repo_header(repo_name, color)
    
    # Check if gh CLI is available
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        typer.echo("  Error: GitHub CLI (gh) is not installed or not in PATH.", err=True)
        typer.echo("  Install it: https://cli.github.com/", err=True)
        return False
    
    # Get GitHub repo URL for display
    repo_url = get_github_repo_url(repo_path)
    if repo_url:
        pr_url = f"{repo_url}/pull/{pr_number}"
        typer.echo(f"  PR URL: {pr_url}")
    
    typer.echo(f"  Checking out PR #{pr_number}...")
    
    # Use gh pr checkout to checkout the PR branch
    # This will fetch and checkout the PR, and the GitHub PR extension will detect it
    cmd = ["gh", "pr", "checkout", str(pr_number)]
    res = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    
    if res.returncode == 0:
        typer.echo("  ✓ Checked out PR branch")
        # Show the output which includes branch name
        if res.stdout.strip():
            for line in res.stdout.strip().split('\n'):
                if line:
                    typer.echo(f"    {line}")
        typer.echo()
        typer.echo("  The PR is now open in your workspace.")
        typer.echo("  Use the GitHub Pull Requests extension in Cursor to view details.")
        return True
    else:
        typer.echo(f"  ✗ Failed to checkout PR: {res.stderr.strip()}", err=True)
        return False

def reset_hard_origin(repo_path: Path, branch: str, repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    # Fetch origin first to ensure we have the latest
    fetch_res = run_git(repo_path, ["fetch", "origin"], capture_output=False)
    if fetch_res.returncode != 0:
        typer.echo("Git fetch failed", err=True)
        return

    res = run_git(repo_path, ["reset", "--hard", f"origin/{branch}"], capture_output=True)
    if res.returncode == 0:
        typer.echo(f"Reset hard to origin/{branch}")
        # Show status after reset
        status_res = run_git(repo_path, ["status", "-sb"], capture_output=True)
        if status_res.returncode == 0:
             for line in status_res.stdout.splitlines():
                typer.echo(line)
    else:
        typer.echo(f"Failed to reset hard to origin/{branch}: {res.stderr.strip()}", err=True)

def run_git_passthrough(repo_path: Path, args: List[str], repo_name: str = "", color: str = "white"):
    if repo_name:
        print_repo_header(repo_name, color)
    
    # Use capture_output=False to let git use pager/interactive mode
    run_git(repo_path, args, capture_output=False)
