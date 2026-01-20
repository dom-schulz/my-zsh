import os
from pathlib import Path
from typing import List, Dict, Any
from . import config

def get_workspace_root() -> Path:
    """Returns the current working directory as the workspace root."""
    return Path.cwd()

def check_repo_exists(repo_name: str) -> bool:
    """Checks if a repo directory exists and is a git repo."""
    root = get_workspace_root()
    repo_path = root / repo_name
    git_path = repo_path / ".git"
    return repo_path.is_dir() and git_path.is_dir()

def get_repos(conf: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Returns the list of configured repositories."""
    return conf.get("repositories", [])

def get_repo_by_alias_or_name(conf: Dict[str, Any], selector: str) -> Dict[str, Any]:
    """Finds a repo by alias or name."""
    repos = get_repos(conf)
    for repo in repos:
        if repo.get("alias") == selector or repo.get("name") == selector:
            return repo
    return None
