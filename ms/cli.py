import typer
import sys
from typing import Optional, Dict, Any
from pathlib import Path
from . import config, workspace, preflight, envfile, exitcodes

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
            
        # Global env alias? "ms env ls" -> maybe "menv"?
        # User asked for "env ls", but "env" is a standard unix command.
        # Overriding "env" is dangerous.
        # Let's verify what the user asked: "run 'cs env ls' and 'env ls'"
        # Overriding 'env' is bad practice. I will not output alias env='ms env'.
        # I will output the repo aliases which enable "cs env ls".
        
    except Exception:
        # Fail silently if config invalid, so shell startup doesn't break
        pass

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
