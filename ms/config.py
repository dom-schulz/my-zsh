import json
import os
import copy
from pathlib import Path
from typing import List, Dict, Any, Optional
import typer
from . import exitcodes

CONFIG_FILENAME = "ms-config.json"

DEFAULT_CONFIG = {
    "schemaVersion": 1,
    "workspace": {
        "name": "default",
        "repoDiscovery": "immediate-children-git-only"
    },
    "env": {
        "mode": "strict",
        "missingEnvFile": "warn",
        "ignoreKeys": [],
        "matchGroups": []
    },
    "repositories": []
}

def get_config_path() -> Path:
    """Returns the path to ms-config.json in the current directory."""
    return Path.cwd() / CONFIG_FILENAME

def load_config(require_config: bool = True) -> Dict[str, Any]:
    """
    Loads and validates the configuration file.
    
    Args:
        require_config: If True, raises FileNotFoundError if config is missing.
                       If False, returns default config if missing.
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        if require_config:
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
            
        # Return defaults if missing, so setup can work on a fresh state
        return copy.deepcopy(DEFAULT_CONFIG)

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        typer.echo(f"ms-config.json invalid JSON: {e}", err=True)
        raise typer.Exit(code=exitcodes.PREFLIGHT_ERROR)

    if config.get("schemaVersion") != 1:
        typer.echo(f"Unsupported schemaVersion: {config.get('schemaVersion')}", err=True)
        raise typer.Exit(code=exitcodes.PREFLIGHT_ERROR)
        
    return config

def save_config(config: Dict[str, Any]) -> None:
    """Saves the configuration file."""
    config_path = get_config_path()
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
            f.write("\n") # Ensure trailing newline
    except OSError as e:
        typer.echo(f"Failed to save ms-config.json: {e}", err=True)
        raise typer.Exit(code=exitcodes.IO_ERROR)
