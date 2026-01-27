import subprocess
import os
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import typer
from . import envfile


def get_venv_alembic(repo_path: Path) -> Path:
    """Get path to alembic executable in repo's venv."""
    venv_alembic = repo_path / ".venv" / "bin" / "alembic"
    if not venv_alembic.exists():
        raise FileNotFoundError(
            f"Alembic not found in venv at {repo_path}. "
            "Run 'ms venv sync' first to set up the virtual environment."
        )
    return venv_alembic


def run_alembic_command(
    repo_path: Path, 
    args: List[str], 
    capture_output: bool = True,
    check: bool = True,
    timeout: int = 10,
    env_file: str = ".env"
) -> subprocess.CompletedProcess:
    """Execute an alembic command using the repo's venv."""
    venv_alembic = get_venv_alembic(repo_path)
    venv_path = repo_path / ".venv"
    
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv_path)
    
    # Load .env file to get database connection settings
    env_path = repo_path / env_file
    if env_path.exists():
        env_vars = envfile.parse_env(env_path)
        # Merge env file variables into environment
        for key, value in env_vars.items():
            # Strip quotes from values
            value = value.strip()
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            env[key] = value
    
    try:
        result = subprocess.run(
            [str(venv_alembic)] + args,
            cwd=repo_path,
            env=env,
            capture_output=capture_output,
            text=True,
            check=check,
            timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Alembic command timed out after {timeout}s. Check database connection.")
    except subprocess.CalledProcessError as e:
        if check:
            raise RuntimeError(f"Alembic command failed: {e.stderr}") from e
        return e


def get_current_db_revision(repo_path: Path) -> Optional[str]:
    """Query the current database revision from alembic_version table."""
    try:
        result = run_alembic_command(
            repo_path, 
            ["current"], 
            capture_output=True,
            check=False,
            timeout=25
        )
        if result.returncode == 0:
            # Parse output: typically "Current revision: abc123def456 (head)"
            output = result.stdout.strip()
            for line in output.splitlines():
                if line and not line.startswith("INFO"):
                    # Extract revision ID (first word after whitespace)
                    parts = line.split()
                    for part in parts:
                        # Revision IDs are typically 12 chars alphanumeric
                        if len(part) >= 12 and part.isalnum():
                            return part
            return None
        else:
            # Try to recover revision from error message if possible
            # Error: ... Can't locate revision identified by 'aaaaaaaaaaa7'
            if result.stderr:
                import re
                match = re.search(r"Can't locate revision identified by '([a-zA-Z0-9]+)'", result.stderr)
                if match:
                    return match.group(1)
            
            typer.echo(f"Warning: Alembic current command failed.", err=True)
            if result.stderr:
                typer.echo(f"Error: {result.stderr.strip()}", err=True)
            return None
    except RuntimeError as e:
        typer.echo(f"Warning: Could not get current DB revision: {e}", err=True)
        return None
    except Exception as e:
        typer.echo(f"Warning: Unexpected error checking DB revision: {e}", err=True)
        return None


def get_revisions_in_branch(
    repo_path: Path, 
    branch_name: str, 
    revisions_dir: str
) -> List[Dict[str, str]]:
    """
    Get ordered list of revision files in a branch.
    Returns list of dicts with 'id' and 'down_revision' keys.
    """
    # Strip trailing slash from revisions_dir
    revisions_dir = revisions_dir.rstrip('/')

    # Use git ls-tree on the tree object directly to be non-recursive
    # This matches standard Alembic behavior (unless recursive_version_locations is set)
    # and prevents finding "archived" migrations in subdirectories.
    # Syntax: git ls-tree --name-only branch:path
    result = subprocess.run(
        ["git", "ls-tree", "--name-only", f"{branch_name}:{revisions_dir}"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return []
    
    revision_files = [
        f for f in result.stdout.splitlines() 
        if f.endswith('.py') and not f.endswith('__init__.py')
    ]
    
    # Parse each revision file to get ID and down_revision
    revisions = []
    for filename in revision_files:
        # Construct full relative path for git show
        rel_path = f"{revisions_dir}/{filename}"
        
        # Get file content from git
        content_result = subprocess.run(
            ["git", "show", f"{branch_name}:{rel_path}"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if content_result.returncode != 0:
            continue
        
        content = content_result.stdout
        revision_id = None
        down_revision = None
        
        # Parse the revision and down_revision from file content
        for line in content.splitlines():
            line = line.strip()
            # Handle both formats:
            # Old: revision = 'abc123'
            # New: revision: str = "abc123"
            if line.startswith("revision:") or line.startswith("revision ="):
                # Extract value after the = sign
                if "=" in line:
                    revision_id = line.split("=", 1)[1].strip().strip("'\"")
            elif line.startswith("down_revision:") or line.startswith("down_revision ="):
                if "=" in line:
                    value = line.split("=", 1)[1].strip().strip("'\"")
                    down_revision = value if value != "None" else None
        
        if revision_id:
            revisions.append({
                "id": revision_id,
                "down_revision": down_revision,
                "file": rel_path
            })
    
    return revisions


def build_revision_chain(revisions: List[Dict[str, str]]) -> List[str]:
    """
    Build ordered chain of revision IDs from base to head.
    Returns list of revision IDs in chronological order.
    """
    if not revisions:
        return []
    
    # Build lookup dict
    rev_lookup = {r["id"]: r for r in revisions}
    
    # Find head (revision with no child)
    children = {r["down_revision"] for r in revisions if r["down_revision"]}
    head = None
    for r in revisions:
        if r["id"] not in children:
            head = r["id"]
            break
    
    if not head:
        # Fallback: use any revision
        head = revisions[0]["id"]
    
    # Walk backwards from head to build chain
    chain = []
    current = head
    visited = set()
    
    while current and current in rev_lookup:
        if current in visited:
            # Circular reference, break
            break
        chain.insert(0, current)
        visited.add(current)
        current = rev_lookup[current]["down_revision"]
    
    return chain


def find_common_revision(
    current_revisions: List[Dict[str, str]], 
    target_revisions: List[Dict[str, str]]
) -> Optional[str]:
    """
    Find the last common revision between two branches.
    Returns the revision ID to downgrade to, or None if no common revision.
    """
    current_chain = build_revision_chain(current_revisions)
    target_chain = build_revision_chain(target_revisions)
    
    # Find last common element
    common = None
    for curr_id in current_chain:
        if curr_id in target_chain:
            common = curr_id
    
    return common


def find_revision_in_branches(
    repo_path: Path,
    revision_id: str,
    revisions_dir: str
) -> List[str]:
    """
    Search all local branches for a specific revision ID.
    Returns list of branch names containing the revision.
    """
    found_branches = []
    
    # Get all local branches
    try:
        result = subprocess.run(
            ["git", "branch", "--format=%(refname:short)"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            return []
            
        branches = [b.strip() for b in result.stdout.splitlines() if b.strip()]
        
        for branch in branches:
            try:
                # Check if revision exists in this branch
                revisions = get_revisions_in_branch(repo_path, branch, revisions_dir)
                if any(r["id"] == revision_id for r in revisions):
                    found_branches.append(branch)
            except Exception:
                continue
                
    except Exception:
        pass
            
    return found_branches


def check_revisions_changed(
    repo_path: Path, 
    current_branch: str, 
    target_branch: str, 
    revisions_dir: str
) -> bool:
    """Check if revision files changed between two branches."""
    result = subprocess.run(
        ["git", "diff", "--quiet", current_branch, target_branch, "--", revisions_dir],
        cwd=repo_path
    )
    # Exit code 0 = no changes, 1 = changes exist
    return result.returncode != 0


def get_migration_plan(
    repo_path: Path,
    current_branch: str,
    target_branch: str,
    revisions_dir: str
) -> Optional[Dict]:
    """
    Generate a migration plan for branch switch.
    Returns dict with migration details or None if no migration needed.
    Returns dict with 'error' key if there was a problem.
    """
    # Note: We previously used check_revisions_changed() here to optimize,
    # but it proved unreliable (git diff returning 0 when files would change).
    # We now always calculate the plan to ensure safety.
    
    # Get current DB state
    current_db_rev = get_current_db_revision(repo_path)
    if not current_db_rev:
        return {
            "error": "Could not determine current database revision. Database may be unreachable."
        }
    
    # Get revisions in both branches
    current_revisions = get_revisions_in_branch(repo_path, current_branch, revisions_dir)
    target_revisions = get_revisions_in_branch(repo_path, target_branch, revisions_dir)
    
    if not current_revisions and not target_revisions:
        # No revisions in either branch
        return None
        
    # Check if current_db_rev is a "ghost" revision (not in current branch)
    # This happens if we are on a branch that doesn't have the current migration file
    current_rev_ids = {r["id"] for r in current_revisions}
    target_rev_ids = {r["id"] for r in target_revisions}
    
    is_ghost = current_db_rev not in current_rev_ids
    
    if is_ghost:
        if current_db_rev in target_rev_ids:
            # Move to the branch that has this revision.
            # No downgrade needed.
            # Just check if we need to upgrade to target head.
            target_chain = build_revision_chain(target_revisions)
            target_head = target_chain[-1] if target_chain else None
            
            return {
                "current_db_revision": current_db_rev,
                "common_revision": None, 
                "target_head_revision": target_head,
                "needs_downgrade": False,
                "needs_upgrade": bool(target_head and target_head != current_db_rev)
            }
        else:
            # Ghost revision is not in target either.
            # We can't downgrade because we don't have the file.
            
            # Search for the revision in other branches
            found_branches = find_revision_in_branches(repo_path, current_db_rev, revisions_dir)
            
            return {
                "error": f"Database is at revision {current_db_rev}, which is missing from both current and target branches. Cannot calculate migration path.",
                "missing_revision": current_db_rev,
                "found_in_branches": found_branches
            }
    
    # Find common revision
    common_rev = find_common_revision(current_revisions, target_revisions)
    
    # Build chains to determine if we're ahead or behind
    current_chain = build_revision_chain(current_revisions)
    target_chain = build_revision_chain(target_revisions)
    target_head = target_chain[-1] if target_chain else None
    
    # Determine if we need to downgrade: only if current DB is ahead of common revision
    needs_downgrade = False
    if common_rev and current_db_rev != common_rev:
        # Check if current_db_rev is in the current chain after the common_rev
        # This means the current branch is ahead and needs to downgrade
        try:
            common_idx = current_chain.index(common_rev)
            current_idx = current_chain.index(current_db_rev)
            needs_downgrade = current_idx > common_idx
        except ValueError:
            # If either revision is not in the chain, fall back to simple comparison
            needs_downgrade = True
    
    return {
        "current_db_revision": current_db_rev,
        "common_revision": common_rev,
        "target_head_revision": target_head,
        "needs_downgrade": needs_downgrade,
        "needs_upgrade": bool(target_head and target_head != current_db_rev)
    }


def execute_migration(
    repo_path: Path,
    downgrade_to: Optional[str],
    upgrade: bool = True
) -> Tuple[bool, str]:
    """
    Execute database migration.
    Returns (success, error_message) tuple.
    """
    try:
        # Downgrade if needed
        if downgrade_to:
            typer.echo(f"Downgrading to revision: {downgrade_to}")
            result = run_alembic_command(
                repo_path, 
                ["downgrade", downgrade_to],
                capture_output=True,
                check=True,
                timeout=30  # Longer timeout for actual migrations
            )
            typer.echo("Downgrade complete")
        
        # Upgrade if needed
        if upgrade:
            typer.echo("Upgrading to head...")
            result = run_alembic_command(
                repo_path,
                ["upgrade", "head"],
                capture_output=True,
                check=True,
                timeout=30  # Longer timeout for actual migrations
            )
            typer.echo("Upgrade complete")
        
        return True, ""
    
    except RuntimeError as e:
        return False, str(e)
    except FileNotFoundError as e:
        return False, str(e)
