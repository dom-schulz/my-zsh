# Completion functions for custom git utilities
# These provide intelligent autocompletion for branch names, files, etc.

# Helper function to get local branch names
_git_local_branches() {
    local branches
    branches=(${(f)"$(git branch 2>/dev/null | sed 's/^[* ] //')"})
    _describe 'local branches' branches
}

# Helper function to get remote branch names (without origin/ prefix)
_git_remote_branches() {
    local branches
    branches=(${(f)"$(git branch -r 2>/dev/null | grep -v '\->' | sed 's/^[* ] *origin\///' | sed 's/^[* ] *//')"})
    _describe 'remote branches' branches
}

# Helper function to get all branch names (local + remote)
_git_all_branches() {
    local branches
    local local_branches=(${(f)"$(git branch 2>/dev/null | sed 's/^[* ] //')"})
    local remote_branches=(${(f)"$(git branch -r 2>/dev/null | grep -v '\->' | sed 's/^[* ] *origin\///' | sed 's/^[* ] *//')"})
    
    # Combine and deduplicate
    branches=(${(u)local_branches} ${(u)remote_branches})
    _describe 'branches' branches
}

# Helper function to get modified/staged files
_git_modified_files() {
    local files
    files=(${(f)"$(git diff --name-only 2>/dev/null; git diff --cached --name-only 2>/dev/null)"})
    _files -g "${files[@]}"
}

# Completion for gco (git checkout) - local and remote branches
_gco() {
    _git_all_branches
}

# Completion for grho (git reset hard origin) - remote branches
_grho() {
    _git_remote_branches
}

# Completion for gbD (git branch -D) - local branches only
_gbD() {
    _git_local_branches
}

# Completion for gr (git restore) - modified files
_gr() {
    _git_modified_files
}

# Register completion functions
compdef _gco gco
compdef _grho grho
compdef _gbD gbD
compdef _gr gr

