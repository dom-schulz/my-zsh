import typer
import sys
from typing import Optional, Dict, Any, List
from pathlib import Path
from . import config, workspace, preflight, envfile, exitcodes, git_ops

app = typer.Typer(help="Multi-service workspace management tool")

@app.callback()
def main(ctx: typer.Context):
    """
    Global preflight checks.
    """
    # Preflight checks handle missing config/repos, 
    # but we skip them for 'setup' command inside the preflight module.
    try:
        preflight.run_checks(ctx)
    except typer.Exit as e:
        raise e
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(code=1)

@app.command()
def setup():
    """
    Interactive setup menu.
    """
    # Simple interactive loop
    while True:
        typer.echo("\n--- ms setup ---")
        choices = ["Add repo", "Modify repo", "Remove repo", "Modify env rules", "Exit"]
        for idx, choice in enumerate(choices, 1):
            typer.echo(f"{idx}. {choice}")
        
        selection = typer.prompt("Select option (0 to exit)", type=int, default=len(choices))
        
        if selection == len(choices) or selection == 0: # Exit
            break
        elif selection == 1: # Add repo
            setup_add_repo()
        elif selection == 2: # Modify repo
            setup_modify_repo()
        elif selection == 3: # Remove repo
            setup_remove_repo()
        elif selection == 4: # Modify env rules
            setup_modify_env_rules()
        else:
            typer.echo("Invalid selection")

    # Run health check at end
    try:
        typer.echo("\nRunning health checks...")
        # create a dummy context for preflight checks
        # Actually preflight.run_checks checks everything.
        # We can just call the logic manually or reload config.
        conf = config.load_config()
        workspace.get_repos(conf) # Just ensures parsing works
        typer.echo("Health check passed.")
    except Exception as e:
        typer.echo(f"Health check warning: {e}")

@app.command()
def aliases():
    """
    Output shell aliases for configured repos.
    Usage in .zshrc: eval "$(ms aliases)"
    """
    try:
        conf = config.load_config()
        repos = workspace.get_repos(conf)
        
        # Repo aliases
        for repo in repos:
            alias = repo["alias"]
            # alias cs='ms cs'
            typer.echo(f"alias {alias}='ms {alias}'")
        
        # Git aliases
        typer.echo("alias gst='ms gst'")
        typer.echo("alias gco='ms gco'")
        typer.echo("alias gfo='ms gfo'")
        typer.echo("alias gpu='ms gpu'")
        typer.echo("alias gcob='ms gcob'")
        typer.echo("alias gba='ms gba'")
        typer.echo("alias ga='ms ga'")
        typer.echo("alias gcm='ms gcm'")
        typer.echo("alias gp='ms gp'")
        typer.echo("alias gfp='ms gfp'")
        typer.echo("alias gd='ms gd'")
            
    except Exception:
        # Fail silently if config invalid, so shell startup doesn't break
        pass

@app.command()
def completion():
    """
    Output zsh completion configuration.
    Usage in .zshrc: eval "$(ms completion)"
    """
    completion_script = '''# ms completion for zsh
# Cache repos at load time (repos don't change often)
typeset -ga _MS_CACHED_REPOS
_MS_CACHED_REPOS=(${(f)"$(ms list-repos 2>/dev/null)"})

# Helper to get all branches (refreshed each time)
_ms_all_branches() {
    local -a branches
    branches=(${(f)"$(ms list-branches 2>/dev/null)"})
    compadd -a branches
}

# Helper to get branches from a specific repo
_ms_branches_for_repo() {
    local repo_alias=$1
    local -a branches
    branches=(${(f)"$(ms list-branches-for-repo "$repo_alias" 2>/dev/null)"})
    compadd -a branches
}

_gco() {
    local curcontext="$curcontext" state line
    typeset -A opt_args
    
    # Check if we're completing right after -r or --repo
    if [[ "${words[CURRENT-1]}" == "-r" || "${words[CURRENT-1]}" == "--repo" ]]; then
        # Complete repo names
        compadd -a _MS_CACHED_REPOS
        return
    fi
    
    # Parse the command line to find if -r/--repo was already specified
    local repo_specified=""
    local i
    for ((i=2; i < CURRENT; i++)); do
        if [[ "${words[i]}" == "-r" || "${words[i]}" == "--repo" ]]; then
            if (( i < $#words )); then
                repo_specified="${words[i+1]}"
                break
            fi
        fi
    done
    
    # Complete branch names
    if [[ -n "$repo_specified" ]]; then
        # Complete branches from specific repo (always fresh)
        _ms_branches_for_repo "$repo_specified"
    else
        # Complete all branches (always fresh)
        _ms_all_branches
    fi
}

_gcob() {
    _arguments \\
        '1:branch name:' \\
        '--push[Push branch]' \\
        '*'{-r,--repo}'=:repo:_ms_repos'
}

_gst() {
    _arguments \\
        '*'{-r,--repo}'=:repo:_ms_repos'
}

_gba() {
    _arguments \\
        '*'{-r,--repo}'=:repo:_ms_repos'
}

_gfo() {
    _arguments \\
        '*'{-r,--repo}'=:repo:_ms_repos'
}

_gpu() {
    _arguments \\
        '*'{-r,--repo}'=:repo:_ms_repos'
}

_ga() {
    _arguments \\
        '*'{-r,--repo}'=:repo:_ms_repos'
}

_gcm() {
    _arguments \\
        '1:message:' \\
        '*'{-r,--repo}'=:repo:_ms_repos'
}

_gp() {
    _arguments \\
        '--force[Force push]' \\
        '*'{-r,--repo}'=:repo:_ms_repos'
}

_gfp() {
    _arguments \\
        '--force[Required to execute]' \\
        '*'{-r,--repo}'=:repo:_ms_repos'
}

_gd() {
    _arguments \\
        '*'{-r,--repo}'=:repo:_ms_repos' \\
        '*:git diff args:'
}

# Register completions
# Note: These must be registered AFTER the aliases are defined
# Use compdef -d first to clear any existing completion, then register
compdef -d gco 2>/dev/null; compdef _gco gco
compdef -d gcob 2>/dev/null; compdef _gcob gcob
compdef -d gst 2>/dev/null; compdef _gst gst
compdef -d gba 2>/dev/null; compdef _gba gba
compdef -d gfo 2>/dev/null; compdef _gfo gfo
compdef -d gpu 2>/dev/null; compdef _gpu gpu
compdef -d ga 2>/dev/null; compdef _ga ga
compdef -d gcm 2>/dev/null; compdef _gcm gcm
compdef -d gp 2>/dev/null; compdef _gp gp
compdef -d gfp 2>/dev/null; compdef _gfp gfp
compdef -d gd 2>/dev/null; compdef _gd gd

# Mark that completions are loaded
typeset -g _MS_COMPLETIONS_LOADED=1
'''
    typer.echo(completion_script)

@app.command()
def list_branches():
    """
    List all unique branch names across repos (for completion).
    """
    try:
        conf = config.load_config()
        repos = workspace.get_repos(conf)
        root = workspace.get_workspace_root()
        
        branches = set()
        for r in repos:
            path = root / r["name"]
            # Get local branches
            res = git_ops.run_git(path, ["branch", "--format=%(refname:short)"], capture_output=True)
            if res.returncode == 0:
                for branch in res.stdout.strip().split('\n'):
                    if branch:
                        branches.add(branch.strip())
            
            # Get remote branches (without remotes/origin/ prefix)
            res = git_ops.run_git(path, ["branch", "-r", "--format=%(refname:short)"], capture_output=True)
            if res.returncode == 0:
                for branch in res.stdout.strip().split('\n'):
                    if branch and branch.startswith('origin/'):
                        branch_name = branch.replace('origin/', '', 1)
                        if branch_name != 'HEAD':
                            branches.add(branch_name)
        
        for branch in sorted(branches):
            typer.echo(branch)
            
    except Exception:
        # Fail silently for completion
        pass

@app.command()
def list_repos():
    """
    List all repo aliases (for completion).
    """
    try:
        conf = config.load_config()
        repos = workspace.get_repos(conf)
        
        for repo in repos:
            typer.echo(repo["alias"])
            
    except Exception:
        # Fail silently for completion
        pass

@app.command()
def list_branches_for_repo(repo_alias: str):
    """
    List branches for a specific repo (for completion).
    """
    try:
        conf = config.load_config()
        all_repos = workspace.get_repos(conf)
        repo = next((r for r in all_repos if r["alias"] == repo_alias), None)
        
        if not repo:
            return
        
        root = workspace.get_workspace_root()
        path = root / repo["name"]
        
        if not path.exists():
            return
        
        branches = set()
        
        # Get local branches
        res = git_ops.run_git(path, ["branch", "--format=%(refname:short)"], capture_output=True)
        if res.returncode == 0:
            for branch in res.stdout.strip().split('\n'):
                if branch:
                    branches.add(branch.strip())
        
        # Get remote branches (without remotes/origin/ prefix)
        res = git_ops.run_git(path, ["branch", "-r", "--format=%(refname:short)"], capture_output=True)
        if res.returncode == 0:
            for branch in res.stdout.strip().split('\n'):
                if branch and branch.startswith('origin/'):
                    branch_name = branch.replace('origin/', '', 1)
                    if branch_name != 'HEAD':
                        branches.add(branch_name)
        
        for branch in sorted(branches):
            typer.echo(branch)
            
    except Exception:
        # Fail silently for completion
        pass

# --- Git Commands ---

def resolve_repos(conf: Dict[str, Any], aliases: Optional[List[str]] = None, required: bool = False) -> List[Dict[str, Any]]:
    all_repos = workspace.get_repos(conf)
    if not aliases:
        if required:
             typer.echo("Error: Repo argument required for this command.", err=True)
             raise typer.Exit(code=2)
        return all_repos
    
    target_repos = []
    for alias in aliases:
        repo = next((r for r in all_repos if r["alias"] == alias), None)
        if not repo:
             typer.echo(f"Unknown repo '{alias}'", err=True)
             raise typer.Exit(code=2)
        target_repos.append(repo)
    return target_repos

@app.command()
def gst(repo: Optional[List[str]] = typer.Option(None, "--repo", "-r", help="Repo alias(es)")):
    """Git status"""
    conf = config.load_config()
    repos = resolve_repos(conf, repo)
    root = workspace.get_workspace_root()
    
    for r in repos:
        git_ops.print_status(r["name"], root / r["name"], r.get("color", "white"))
        
@app.command()
def gco(branch: str, repo: Optional[List[str]] = typer.Option(None, "--repo", "-r", help="Repo alias(es)")):
    """Git checkout"""
    conf = config.load_config()
    root = workspace.get_workspace_root()
    
    if repo:
        # Targeted checkout
        repos = resolve_repos(conf, repo)
        for r in repos:
            path = root / r["name"]
            git_ops.fetch_origin(path)
            git_ops.checkout(path, branch, r["name"], r.get("color", "white"))
    else:
        # Discovery mode
        repos = workspace.get_repos(conf)
        candidates = []
        for r in repos:
            path = root / r["name"]
            git_ops.fetch_origin(path)
            # Check if branch exists (remote or local)
            res = git_ops.run_git(path, ["rev-parse", "--verify", branch], capture_output=True)
            res_remote = git_ops.run_git(path, ["rev-parse", "--verify", f"origin/{branch}"], capture_output=True)
            
            if res.returncode == 0 or res_remote.returncode == 0:
                 candidates.append(r)
        
        if not candidates:
            typer.echo(f"Branch '{branch}' not found in any repo.")
            return

        # Build colored alias list
        try:
            from rich.console import Console
            from rich.text import Text
            
            console = Console()
            
            # Build the message with colors
            message = Text("Branch '")
            message.append(branch, style="bold")
            message.append("' found in: ")
            
            for i, r in enumerate(candidates):
                if i > 0:
                    message.append(", ")
                message.append(r['alias'], style=r.get("color", "white"))
            
            console.print(message)
        except ImportError:
            # Fallback without colors
            typer.echo(f"Branch '{branch}' found in: {', '.join(r['alias'] for r in candidates)}")
        
        if typer.confirm("Switch these repos?"):
             for r in candidates:
                 git_ops.checkout(root / r["name"], branch, r["name"], r.get("color", "white"))

@app.command()
def gfo(repo: Optional[List[str]] = typer.Option(None, "--repo", "-r", help="Repo alias(es)")):
    """Git fetch origin"""
    conf = config.load_config()
    repos = resolve_repos(conf, repo)
    root = workspace.get_workspace_root()
    for r in repos:
        git_ops.fetch_origin(root / r["name"], r["name"], r.get("color", "white"))

@app.command()
def gpu(repo: Optional[List[str]] = typer.Option(None, "--repo", "-r", help="Repo alias(es)")):
    """Git pull"""
    conf = config.load_config()
    repos = resolve_repos(conf, repo)
    root = workspace.get_workspace_root()
    for r in repos:
        git_ops.pull(root / r["name"], r["name"], r.get("color", "white"))

@app.command()
def gcob(branch: str, push: bool = False, repo: Optional[List[str]] = typer.Option(None, "--repo", "-r", help="Repo alias(es)")):
    """Git checkout -b"""
    conf = config.load_config()
    repos = resolve_repos(conf, repo)
    root = workspace.get_workspace_root()
    for r in repos:
        git_ops.create_branch(root / r["name"], branch, push, r["name"], r.get("color", "white"))

@app.command()
def gba(repo: Optional[List[str]] = typer.Option(None, "--repo", "-r", help="Repo alias(es)")):
    """Git branch -a"""
    conf = config.load_config()
    repos = resolve_repos(conf, repo)
    root = workspace.get_workspace_root()
    for r in repos:
        git_ops.branch_all(root / r["name"], r["name"], r.get("color", "white"))

@app.command()
def ga(repo: List[str] = typer.Option(..., "--repo", "-r", help="Repo alias(es)")):
    """Git add ."""
    conf = config.load_config()
    repos = resolve_repos(conf, repo, required=True)
    root = workspace.get_workspace_root()
    for r in repos:
        git_ops.add_all(root / r["name"], r["name"], r.get("color", "white"))

@app.command()
def gcm(message: str, repo: List[str] = typer.Option(..., "--repo", "-r", help="Repo alias(es)")):
    """Git commit -m"""
    conf = config.load_config()
    repos = resolve_repos(conf, repo, required=True)
    root = workspace.get_workspace_root()
    for r in repos:
        git_ops.commit(root / r["name"], message, r["name"], r.get("color", "white"))

@app.command()
def gp(force: bool = False, repo: List[str] = typer.Option(..., "--repo", "-r", help="Repo alias(es)")):
    """Git push"""
    conf = config.load_config()
    repos = resolve_repos(conf, repo, required=True)
    root = workspace.get_workspace_root()
    for r in repos:
        git_ops.push(root / r["name"], force, r.get("defaultBranch", "main"), r["name"], r.get("color", "white"))

@app.command()
def gfp(force: bool = typer.Option(False, "--force", help="Required to execute"), repo: List[str] = typer.Option(..., "--repo", "-r", help="Repo alias(es)")):
    """Git fetch --prune and delete gone branches"""
    conf = config.load_config()
    repos = resolve_repos(conf, repo, required=True)
    root = workspace.get_workspace_root()
    for r in repos:
        git_ops.fetch_prune_delete(root / r["name"], force, r["name"], r.get("color", "white"))

@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def gd(ctx: typer.Context, repo: List[str] = typer.Option(..., "--repo", "-r", help="Repo alias(es)")):
    """Git diff (passes extra args to git diff)"""
    conf = config.load_config()
    repos = resolve_repos(conf, repo, required=True)
    root = workspace.get_workspace_root()
    
    # Only allow single repo for interactive diff usually, but loop is fine
    for r in repos:
        git_ops.diff(root / r["name"], ctx.args, r["name"], r.get("color", "white"))

# --- Setup Helpers ---

def prompt_for_color() -> str:
    colors = {
        "1": "blue",
        "2": "green",
        "3": "magenta", # Pink/Purple
        "4": "cyan",
        "5": "yellow",
        "6": "#FFA500", # Orange
        "7": "custom"
    }
    typer.echo("\nSelect color:")
    typer.echo("1. Blue")
    typer.echo("2. Green")
    typer.echo("3. Pink/Purple")
    typer.echo("4. Cyan")
    typer.echo("5. Yellow")
    typer.echo("6. Orange")
    typer.echo("7. Custom Hex")
    
    choice = typer.prompt("Select color", type=str, default="1")
    
    if choice in colors and colors[choice] != "custom":
        return colors[choice]
    elif choice == "7" or choice == "custom":
        while True:
            hex_code = typer.prompt("Enter hex code (e.g. #ff00ff)")
            if hex_code.startswith("#") and len(hex_code) == 7:
                return hex_code
            typer.echo("Invalid hex format. Must be #RRGGBB")
    
    return "white" # Fallback

def setup_add_repo():
    root = workspace.get_workspace_root()
    # Discover candidates
    candidates = []
    try:
        for p in root.iterdir():
            if p.is_dir() and (p / ".git").is_dir():
                candidates.append(p.name)
    except OSError:
        pass
    
    conf = config.load_config()
    existing_names = {r["name"] for r in workspace.get_repos(conf)}
    existing_aliases = {r["alias"] for r in workspace.get_repos(conf)}
    
    available = [c for c in candidates if c not in existing_names]
    
    if not available:
        typer.echo("No new git repositories found in workspace root.")
        return

    typer.echo("\nAvailable repositories:")
    for idx, name in enumerate(available, 1):
        typer.echo(f"{idx}. {name}")
    
    choice = typer.prompt("Choose repo to add (0 to cancel)", type=int)
    if choice == 0 or choice > len(available):
        return
        
    repo_name = available[choice - 1]
    
    while True:
        alias = typer.prompt(f"Enter alias for {repo_name}")
        if not alias:
            continue
        if alias in existing_aliases:
            typer.echo(f"Alias '{alias}' already in use.")
            continue
        break
    
    # Show available types
    typer.echo("\nAvailable types: app, db-alembic")
    while True:
        rtype = typer.prompt("Type", default="app")
        
        # Enforce single db-alembic rule
        if rtype == "db-alembic":
            existing_db_repos = [r for r in workspace.get_repos(conf) if r.get("type") == "db-alembic"]
            if existing_db_repos:
                typer.echo(f"Error: A db-alembic repo already exists ({existing_db_repos[0]['name']}). Only one allowed.")
                continue
        break
    
    repo_config = {
        "name": repo_name,
        "alias": alias,
        "type": rtype,
        "envFile": ".env"
    }
    
    env_file = typer.prompt("Env file name", default=".env")
    repo_config["envFile"] = env_file

    default_branch = typer.prompt("Default branch", default="main")
    repo_config["defaultBranch"] = default_branch
    
    if rtype == "db-alembic":
        rev_dir = typer.prompt("Alembic revisions directory")
        repo_config["alembic"] = {"revisionsDirectory": rev_dir}
        
    # Color selection
    repo_config["color"] = prompt_for_color()

    conf.setdefault("repositories", []).append(repo_config)
    config.save_config(conf)
    typer.echo(f"Repo {repo_name} added.")

def setup_modify_repo():
    conf = config.load_config()
    repos = workspace.get_repos(conf)
    if not repos:
        typer.echo("No repositories configured.")
        return
        
    typer.echo("\nConfigured repositories:")
    for idx, r in enumerate(repos, 1):
        typer.echo(f"{idx}. {r['name']} ({r['alias']})")
        
    choice = typer.prompt("Select repo to modify (0 to cancel)", type=int)
    if choice == 0 or choice > len(repos):
        return
        
    repo = repos[choice - 1]
    
    # Modify fields
    new_alias = typer.prompt(f"Alias", default=repo['alias'])
    # Validate uniqueness if changed
    if new_alias != repo['alias']:
        existing_aliases = {r["alias"] for r in repos if r is not repo}
        if new_alias in existing_aliases:
            typer.echo("Alias already in use. Keeping old alias.")
            new_alias = repo['alias']
    repo['alias'] = new_alias
    
    repo['envFile'] = typer.prompt("Env file", default=repo.get('envFile', '.env'))

    repo['defaultBranch'] = typer.prompt("Default branch", default=repo.get('defaultBranch', 'main'))
    
    if repo.get('type') == 'db-alembic':
        current_rev = repo.get('alembic', {}).get('revisionsDirectory', '')
        new_rev = typer.prompt("Revisions directory", default=current_rev)
        if 'alembic' not in repo:
            repo['alembic'] = {}
        repo['alembic']['revisionsDirectory'] = new_rev
        
    # Modify color
    current_color = repo.get('color', 'white')
    typer.echo(f"Current color: {current_color}")
    if typer.confirm("Change color?"):
        repo['color'] = prompt_for_color()

    config.save_config(conf)
    typer.echo("Repo updated.")

def setup_remove_repo():
    conf = config.load_config()
    repos = workspace.get_repos(conf)
    if not repos:
        return

    typer.echo("\nConfigured repositories:")
    for idx, r in enumerate(repos, 1):
        typer.echo(f"{idx}. {r['name']} ({r['alias']})")
        
    choice = typer.prompt("Select repo to remove (0 to cancel)", type=int)
    if choice == 0 or choice > len(repos):
        return
        
    removed = repos.pop(choice - 1)
    config.save_config(conf)
    typer.echo(f"Removed {removed['name']}.")

def setup_modify_env_rules():
    while True:
        conf = config.load_config()
        env_conf = conf.setdefault("env", {})
        
        mode = env_conf.get('mode', 'strict')
        missing_behavior = env_conf.get('missingEnvFile', 'warn')
        ignore_keys = env_conf.get('ignoreKeys', [])
        match_groups = env_conf.get('matchGroups', [])

        typer.echo("\n--- Modify Env Rules ---")
        typer.echo(f"Mode: {mode}")
        typer.echo(f"Missing Env File: {missing_behavior}")
        typer.echo(f"Ignore Keys: {len(ignore_keys)}")
        typer.echo(f"Match Groups: {len(match_groups)}")
        
        choices = [
            "Change Mode (strict/warn)",
            "Change Missing Env File Behavior",
            "Manage Ignore Keys",
            "Manage Match Groups",
            "Back"
        ]
        
        for idx, choice in enumerate(choices, 1):
            typer.echo(f"{idx}. {choice}")
            
        selection = typer.prompt("Select option (0 to exit)", type=int, default=len(choices))
        
        if selection == 0: # Exit setup completely
            raise typer.Exit()
        
        if selection == len(choices): # Back
            break
            
        elif selection == 1: # Change Mode
            env_conf['mode'] = typer.prompt("Mode (strict/warn)", default=mode)
            config.save_config(conf)
            
        elif selection == 2: # Change Missing Env File Behavior
            env_conf['missingEnvFile'] = typer.prompt("Behavior (strict/warn/ignore)", default=missing_behavior)
            config.save_config(conf)
            
        elif selection == 3: # Manage Ignore Keys
            setup_manage_ignore_keys(conf)
            
        elif selection == 4: # Manage Match Groups
            setup_manage_match_groups(conf)

def setup_manage_ignore_keys(conf: Dict[str, Any]):
    while True:
        ignore_keys = conf["env"].get("ignoreKeys", [])
        typer.echo("\n--- Ignore Keys ---")
        if not ignore_keys:
            typer.echo("(No keys ignored)")
        else:
            for idx, key in enumerate(ignore_keys, 1):
                typer.echo(f"{idx}. {key}")
        
        typer.echo("\nOptions:")
        typer.echo("1. Add key")
        typer.echo("2. Remove key")
        typer.echo("3. Back")
        
        choice = typer.prompt("Select option (0 to exit)", type=int, default=3)
        
        if choice == 0:
            raise typer.Exit()
        
        if choice == 3:
            break
        elif choice == 1:
            new_key = typer.prompt("Enter key to ignore")
            if new_key and new_key not in ignore_keys:
                conf["env"].setdefault("ignoreKeys", []).append(new_key)
                config.save_config(conf)
                typer.echo(f"Added {new_key}.")
            elif new_key in ignore_keys:
                typer.echo("Key already ignored.")
        elif choice == 2:
            if not ignore_keys:
                continue
            to_remove = typer.prompt("Select number to remove (0 to cancel)", type=int)
            if 0 < to_remove <= len(ignore_keys):
                removed = ignore_keys.pop(to_remove - 1)
                config.save_config(conf)
                typer.echo(f"Removed {removed}.")

def setup_manage_match_groups(conf: Dict[str, Any]):
    while True:
        groups = conf["env"].get("matchGroups", [])
        typer.echo("\n--- Match Groups ---")
        if not groups:
            typer.echo("(No match groups defined)")
        else:
            for idx, group in enumerate(groups, 1):
                keys_str = ", ".join(group.get("keys", []))
                typer.echo(f"{idx}. {group.get('name')} [{keys_str}]")
        
        typer.echo("\nOptions:")
        typer.echo("1. Add group")
        typer.echo("2. Remove group")
        typer.echo("3. Back")
        
        choice = typer.prompt("Select option (0 to exit)", type=int, default=3)
        
        if choice == 0:
            raise typer.Exit()
        
        if choice == 3:
            break
        elif choice == 1:
            name = typer.prompt("Group name (e.g., 'sql-server')")
            keys_input = typer.prompt("Comma-separated keys (e.g., 'DB_HOST,SQL_SERVER')")
            # Strip quotes and whitespace
            keys = []
            for k in keys_input.split(","):
                clean_key = k.strip()
                if (clean_key.startswith('"') and clean_key.endswith('"')) or \
                   (clean_key.startswith("'") and clean_key.endswith("'")):
                    clean_key = clean_key[1:-1]
                if clean_key:
                    keys.append(clean_key)
            
            if name and keys:
                new_group = {"name": name, "keys": keys}
                conf["env"].setdefault("matchGroups", []).append(new_group)
                config.save_config(conf)
                typer.echo(f"Added group '{name}'.")
            else:
                typer.echo("Invalid input. Name and at least one key required.")
                
        elif choice == 2:
            if not groups:
                continue
            to_remove = typer.prompt("Select number to remove (0 to cancel)", type=int)
            if 0 < to_remove <= len(groups):
                removed = groups.pop(to_remove - 1)
                config.save_config(conf)
                typer.echo(f"Removed group '{removed.get('name')}'.")

# --- Env Command Logic ---

def handle_env_ls(alias: str):
    conf = config.load_config()
    repo = workspace.get_repo_by_alias_or_name(conf, alias)
    if not repo:
        typer.echo(f"Unknown repo '{alias}'", err=True)
        raise typer.Exit(code=exitcodes.PREFLIGHT_ERROR)

    root = workspace.get_workspace_root()
    repo_path = root / repo["name"]
    env_filename = repo.get("envFile", ".env")
    env_path = repo_path / env_filename
    
    missing_policy = conf.get("env", {}).get("missingEnvFile", "warn")
    
    if not env_path.exists():
        if missing_policy == "strict":
            typer.echo(f"Env file missing: {env_path}", err=True)
            raise typer.Exit(code=exitcodes.PREFLIGHT_ERROR)
        elif missing_policy == "warn":
             pass 
        if missing_policy != "ignore":
             typer.echo(f"{repo['name']} {env_path} (missing)")
        return # exit 0

    data = envfile.parse_env(env_path)
    
    # Colorize header
    color = repo.get("color", "black")
    header = f"--- {repo['name']} ({env_filename}) ---"
    
    # Try using rich if available for hex support, else Typer secho
    try:
        from rich.console import Console
        console = Console()
        console.print(header, style=color)
    except ImportError:
        # Fallback for standard colors
        if not color.startswith("#"):
            typer.secho(header, fg=color)
        else:
            typer.echo(header)

    for k in sorted(data.keys()):
        typer.echo(f"{k}={data[k]}")
        
    # Check conflicts
    try:
        envfile.validate_env_rules(conf, workspace.get_repos(conf))
    except typer.Exit as e:
        if e.exit_code == exitcodes.ENV_CONFLICT_ERROR:
            # Re-raise to exit with 4
            raise e

def handle_env_set(alias: str, key: str):
    conf = config.load_config()
    repo = workspace.get_repo_by_alias_or_name(conf, alias)
    if not repo:
        typer.echo(f"Unknown repo '{alias}'", err=True)
        raise typer.Exit(code=exitcodes.PREFLIGHT_ERROR)
        
    root = workspace.get_workspace_root()
    repo_path = root / repo["name"]
    env_filename = repo.get("envFile", ".env")
    env_path = repo_path / env_filename
    
    # Validation
    if not all(c.isalnum() or c == '_' for c in key):
        typer.echo(f"Invalid env key '{key}'. Expected [A-Z0-9_]+.", err=True)
        raise typer.Exit(code=exitcodes.PREFLIGHT_ERROR)

    current_val = ""
    if env_path.exists():
        data = envfile.parse_env(env_path)
        current_val = data.get(key, "")
        if key in data:
            typer.echo(f"Current {key}: {current_val}")
        else:
             typer.echo(f"{key} not set.")
    else:
         typer.echo(f"{key} not set (file missing).")
         
    new_val = typer.prompt(f"Enter new value for {key}", default="", show_default=False)
    
    if new_val == "":
        typer.echo("No changes made.")
        raise typer.Exit(code=0)

    # Update
    try:
        changed = envfile.update_env_key(repo_path, env_filename, key, new_val)
        if changed:
            typer.echo(f"Updated {key}.")
            # Validate after write
            try:
                envfile.validate_env_rules(conf, workspace.get_repos(conf))
            except typer.Exit as e:
                if e.exit_code == exitcodes.ENV_CONFLICT_ERROR:
                    typer.echo("Conflicts detected!", err=True)
                    raise e
        else:
            typer.echo("Value unchanged.")
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"Error updating env: {e}", err=True)
        raise typer.Exit(code=exitcodes.IO_ERROR)


# --- Global Env Command ---

global_env_app = typer.Typer(help="Global environment management")
app.add_typer(global_env_app, name="env")

@global_env_app.command("ls")
def list_all_envs():
    """List environment variables for all repositories."""
    conf = config.load_config()
    repos = workspace.get_repos(conf)
    
    if not repos:
        typer.echo("No repositories configured.")
        return

    for repo in repos:
        # Reuse the logic but suppress some errors if needed?
        # Actually handle_env_ls logic is good, just calling it for each repo alias.
        try:
            handle_env_ls(repo["alias"])
            typer.echo("") # Separator
        except typer.Exit:
            # handle_env_ls raises Exit on missing file (strict) or other errors.
            # In global list, we might want to continue to next repo?
            # Current implementation of handle_env_ls raises Exit.
            # Let's catch it and continue.
            pass

# --- Dynamic Command Registration ---

def create_repo_command(alias_name: str):
    # This factory ensures 'alias_name' is captured correctly in the closure
    repo_app = typer.Typer(help=f"Manage repo {alias_name}")
    
    env_app = typer.Typer(help="Manage environment variables")
    repo_app.add_typer(env_app, name="env")

    @env_app.command("ls")
    def list_env(ctx: typer.Context):
        """List environment variables"""
        handle_env_ls(alias_name)
        
    @env_app.command("set")
    def set_env(ctx: typer.Context, key: str):
        """Set environment variable"""
        handle_env_set(alias_name, key)
        
    return repo_app

# Load config and register commands
try:
    _conf = config.load_config()
    if _conf:
        _repos = workspace.get_repos(_conf)
        for _repo in _repos:
            _alias = _repo["alias"]
            _sub_app = create_repo_command(_alias)
            app.add_typer(_sub_app, name=_alias)
except Exception:
    # If config fails to load here, we just don't register dynamic commands.
    # The preflight check in 'main' will handle reporting the error to the user
    # when they try to run anything.
    pass

if __name__ == "__main__":
    app()
