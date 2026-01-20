import typer
from . import config, workspace, exitcodes

def run_checks(ctx: typer.Context):
    """
    Global preflight checks.
    Skipped for 'setup' command.
    """
    # Skip checks if the command is 'setup'
    if ctx.invoked_subcommand == "setup":
        return

    # 1. Check config existence
    conf_path = config.get_config_path()
    if not conf_path.exists():
        typer.echo("ms-config.json not found. Run: ms setup.", err=True)
        raise typer.Exit(code=exitcodes.PREFLIGHT_ERROR)

    # 2. Load config (includes JSON/Schema validation)
    conf = config.load_config()

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
