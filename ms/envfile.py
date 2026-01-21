import os
import re
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import typer
from . import exitcodes, workspace

# Regex for KEY=VALUE lines
ENV_LINE_REGEX = re.compile(r"^[ \t]*([A-Za-z_][A-Za-z0-9_]*)=(.*)$")

def parse_env(file_path: Path) -> Dict[str, str]:
    """
    Parses an .env file into a dict of KEY -> RAW_VALUE.
    Comments and blank lines are ignored.
    """
    env_vars = {}
    if not file_path.exists():
        return env_vars
        
    try:
        with open(file_path, "r") as f:
            for line in f:
                match = ENV_LINE_REGEX.match(line)
                if match:
                    key, value = match.groups()
                    env_vars[key] = value
    except OSError:
        # Caller handles missing/unreadable files based on policy
        pass
    return env_vars

def normalize_value(value: str) -> str:
    """
    Normalizes a value for comparison:
    - Strips surrounding whitespace
    - Strips surrounding quotes (single or double)
    """
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value

def update_env_key(repo_path: Path, env_filename: str, key: str, new_value: str) -> bool:
    """
    Updates or appends a KEY=VALUE in the repo's env file.
    Returns True if changed, False if no change.
    """
    env_path = repo_path / env_filename
    
    # Read existing
    lines = []
    if env_path.exists():
        try:
            with open(env_path, "r") as f:
                lines = f.readlines()
        except OSError:
            typer.echo(f"Cannot read {env_path}", err=True)
            raise typer.Exit(code=exitcodes.IO_ERROR)
    
    key_found = False
    changed = False
    new_lines = []
    
    # Simple heuristic to quote if needed
    # If the value contains spaces and isn't already quoted, quote it.
    # But the user might provide quotes in the input. 
    # The requirement says: "Otherwise write unquoted (optional: auto-quote if contains spaces)"
    # Writes it as provided, assuming the user knows what they are doing.
    # Sticks to literal string replacement first.
    # "Preserve whether existing value was quoted... Otherwise write unquoted"
    
    for line in lines:
        match = ENV_LINE_REGEX.match(line)
        if match:
            current_key, current_raw_val = match.groups()
            if current_key == key:
                key_found = True
                norm_current = normalize_value(current_raw_val)
                norm_new = normalize_value(new_value)
                
                if norm_current == norm_new:
                    # No logical change
                    new_lines.append(line)
                    continue
                
                changed = True
                # Preserve quoting style
                stripped_val = current_raw_val.strip()
                prefix = line[:line.find(current_key)] # preserve indentation? Regex handles start of line
                # Regex ^[ \t]* captures indentation implicitly if looking at the group start
                # But match.group(0) is the whole match.
                # Reconstruct the line.
                
                # Check for quotes in existing value
                quote_char = ""
                if stripped_val.startswith('"') and stripped_val.endswith('"'):
                    quote_char = '"'
                elif stripped_val.startswith("'") and stripped_val.endswith("'"):
                    quote_char = "'"
                
                # If existing was quoted, wrap new value in those quotes (escaping if needed?)
                # Simplified: just wrap.
                final_val = new_value
                if quote_char:
                    # If new value is not quoted, wrap it
                    if not (new_value.startswith(quote_char) and new_value.endswith(quote_char)):
                         final_val = f"{quote_char}{new_value}{quote_char}"
                
                # Reconstruct line
                # match.start(1) is index of key start.
                # Preserve everything before the key.
                pre_key = line[:match.start(1)]
                new_lines.append(f"{pre_key}{key}={final_val}\n")
                continue
        
        new_lines.append(line)
    
    if not key_found:
        changed = True
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines[-1] += "\n"
        new_lines.append(f"{key}={new_value}\n")
    
    if not changed:
        return False
        
    # Atomic write
    try:
        with tempfile.NamedTemporaryFile("w", dir=repo_path, delete=False) as tf:
            tf.writelines(new_lines)
            temp_path = Path(tf.name)
        
        # Permissions? shutil.copymode?
        if env_path.exists():
            shutil.copymode(env_path, temp_path)
            
        os.replace(temp_path, env_path)
    except OSError as e:
        if 'temp_path' in locals() and temp_path.exists():
            os.unlink(temp_path)
        typer.echo(f"Failed to update env file safely: {e}", err=True)
        raise typer.Exit(code=exitcodes.IO_ERROR)
        
    return True

def find_matching_keys(conf: Dict, repos: List[Dict], target_key: str) -> List[Dict]:
    """
    Finds keys in other repos that should match the target_key.
    Returns a list of dicts:
    [
        {
            "repo": repo_dict,
            "key": key_name,
            "value": current_value,
            "source": "assumed" or "group:group_name"
        }
    ]
    """
    env_config = conf.get("env", {})
    ignore_keys = set(env_config.get("ignoreKeys", []))
    match_groups = env_config.get("matchGroups", [])
    
    if target_key in ignore_keys:
        return []

    matches = []
    
    # Check match groups first
    group_match = None
    target_group_keys = set()
    
    for group in match_groups:
        group_keys = set(group.get("keys", []))
        if target_key in group_keys:
            group_match = group
            target_group_keys = group_keys
            break
            
    root = workspace.get_workspace_root()
    
    for repo in repos:
        repo_name = repo["name"]
        env_file = repo.get("envFile", ".env")
        repo_path = root / repo_name
        env_path = repo_path / env_file
        
        # Parse env only if it exists
        if not env_path.exists():
            continue
            
        raw_env = parse_env(env_path)
        
        found_key = None
        source = None
        
        # 1. Check explicit match group
        if group_match:
            # Find any key from the group in this repo
            for k in target_group_keys:
                if k in raw_env:
                    found_key = k
                    source = f"group:{group_match.get('name')}"
                    break
        
        # 2. Check assumed matching (same key name)
        # Only if not found via group (or if group didn't find anything, but assumed matching usually implies same key name)
        if not found_key and not group_match:
            if target_key in raw_env:
                found_key = target_key
                source = "assumed"
                
        if found_key:
            matches.append({
                "repo": repo,
                "key": found_key,
                "value": raw_env[found_key],
                "source": source
            })
            
    return matches

def validate_env_rules(config_data: Dict, repos_data: List[Dict]) -> None:
    """
    Validates environment consistency across repositories.
    """
    env_config = config_data.get("env", {})
    mode = env_config.get("mode", "strict")
    ignore_keys = set(env_config.get("ignoreKeys", []))
    match_groups = env_config.get("matchGroups", [])
    
    # Gather all envs
    # repo_name -> { key: (value, normalized_value) }
    repo_envs = {}
    
    for repo in repos_data:
        repo_name = repo["name"]
        env_file = repo.get("envFile", ".env")
        root = workspace.get_workspace_root()
        repo_path = root / repo_name
        env_path = repo_path / env_file
        
        raw_env = parse_env(env_path)
        repo_envs[repo_name] = {
            k: (v, normalize_value(v)) 
            for k, v in raw_env.items()
        }

    conflicts = []

    # 1. Assumed matching rule
    # Find all keys present in at least 2 repos (excluding ignored)
    all_keys = set()
    key_counts = {}
    
    for env in repo_envs.values():
        for k in env.keys():
            if k not in ignore_keys:
                all_keys.add(k)
                key_counts[k] = key_counts.get(k, 0) + 1
                
    for k in all_keys:
        if key_counts[k] < 2:
            continue
            
        # Check values
        first_val = None
        first_repo = None
        
        for repo_name, env in repo_envs.items():
            if k in env:
                val = env[k][1] # normalized
                if first_val is None:
                    first_val = val
                    first_repo = repo_name
                elif val != first_val:
                    conflicts.append(
                        f"Conflict for key '{k}': {first_repo}={first_val} vs {repo_name}={val}"
                    )

    # 2. Explicit match groups
    for group in match_groups:
        group_keys = set(group.get("keys", []))
        # Find participating repos (have at least one key from group)
        # And ensure within repo consistency + cross-repo consistency
        
        group_val = None
        group_val_source = None
        
        for repo_name, env in repo_envs.items():
            repo_keys = [k for k in env.keys() if k in group_keys]
            if not repo_keys:
                continue
                
            # Check internal consistency
            first_repo_val = env[repo_keys[0]][1]
            for rk in repo_keys[1:]:
                if env[rk][1] != first_repo_val:
                     conflicts.append(
                        f"Internal conflict in '{repo_name}' for group '{group.get('name')}': {repo_keys[0]}={first_repo_val} vs {rk}={env[rk][1]}"
                    )
            
            # Check cross-repo consistency
            if group_val is None:
                group_val = first_repo_val
                group_val_source = f"{repo_name}.{repo_keys[0]}"
            elif first_repo_val != group_val:
                conflicts.append(
                    f"Group '{group.get('name')}' conflict: {group_val_source}={group_val} vs {repo_name}.{repo_keys[0]}={first_repo_val}"
                )

    if conflicts:
        for c in conflicts:
            typer.echo(c, err=True)
            
        if mode == "strict":
            raise typer.Exit(code=exitcodes.ENV_CONFLICT_ERROR)
