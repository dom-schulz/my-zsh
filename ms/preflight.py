import typer
from . import config, workspace, exitcodes

def run_checks(ctx: typer.Context):
    """
    Global preflight checks.
    Skipped for setup/utility commands.
    """
    # Commands that don't require config to exist
    NO_CONFIG_COMMANDS = [
        "setup", 
        "aliases", 
        "completion", 
        "list-repos", 
        "list-branches", 
        "list-branches-for-repo"
    ]
    
    # Skip checks if the command is in the whitelist
    if ctx.invoked_subcommand in NO_CONFIG_COMMANDS:
        return

    # 1. Check config existence
    conf_path = config.get_config_path()
    if not conf_path.exists():
        # Silent exit with code 127 (command not found)
        # This allows zsh to fall back to other aliases with the same name
        raise typer.Exit(code=127)

    # 2. Load config (includes JSON/Schema validation)
    try:
        conf = config.load_config(require_config=True)
    except FileNotFoundError:
        # Should be caught by check above, but just in case
        raise typer.Exit(code=127)

    # 3. Repo presence check
    repos = workspace.get_repos(conf)
    for repo in repos:
        name = repo["name"]
        if not workspace.check_repo_exists(name):
            typer.echo(f"Configured repo '{name}' missing or not a git repo. Run: ms setup.", err=True)
            raise typer.Exit(code=exitcodes.PREFLIGHT_ERROR)

    # 4. Alias uniqueness check
    aliases = set()
    for repo in repos:
        alias = repo.get("alias")
        if alias in aliases:
            typer.echo(f"Alias '{alias}' is not unique. Run: ms setup.", err=True)
            raise typer.Exit(code=exitcodes.PREFLIGHT_ERROR)
        aliases.add(alias)
