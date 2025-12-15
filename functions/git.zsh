# Git utility functions
# Shortcuts for common git workflows

# Git add, commit, and push with message
# Usage: gacmp "commit message"
gacmp() {
    if [ -z "$1" ]; then
        echo "Error: Commit message required"
        echo "Usage: gacmp \"your commit message\""
        return 1
    fi
    
    git add . && \
    git commit -m "$*" && \
    git push origin "$(git branch --show-current)"
}

# Git add and commit with message
# Usage: gacm "commit message"
gacm() {
    if [ -z "$1" ]; then
        echo "Error: Commit message required"
        echo "Usage: gacm \"your commit message\""
        return 1
    fi
    
    git add . && \
    git commit -m "$*"
}

# Git reset hard to origin branch
# Usage: grho <branch-name>
grho() {
    if [ -z "$1" ]; then
        echo "Error: Branch name required"
        echo "Usage: grho <branch-name>"
        return 1
    fi
    
    echo "WARNING: This will reset hard to origin/$1"
    read -q "REPLY?Continue? (y/n) "
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git reset --hard "origin/$1"
    else
        echo "Cancelled"
        return 1
    fi
}

# Git fetch origin
# Usage: gfo
gfo() {
    git fetch origin
}

# Git pull
# Usage: gp
gp() {
    git pull
}

# Git checkout branch
# Usage: gco <branch-name>
gco() {
    if [ -z "$1" ]; then
        echo "Error: Branch name required"
        echo "Usage: gco <branch-name>"
        return 1
    fi
    
    git checkout "$1"
}

# Git checkout -b (create new branch, push, and set upstream)
# Usage: gcob <new-branch-name>
gcob() {
    if [ -z "$1" ]; then
        echo "Error: Branch name required"
        echo "Usage: gcob <new-branch-name>"
        return 1
    fi
    
    git checkout -b "$1" && \
    git push -u origin "$1"
}

# Git fetch prune (with --force to delete local branches not in origin)
# Usage: gfp [--force]
gfp() {
    if [ "$1" = "--force" ]; then
        echo "Fetching from origin..."
        git fetch origin
        
        echo "Pruning remote tracking branches..."
        git fetch --prune
        
        echo "Deleting local branches not in origin..."
        current_branch=$(git branch --show-current)
        
        # Find and delete branches whose upstream is gone
        git branch -vv | grep ': gone]' | awk '{print $1}' | while read branch; do
            # Skip current branch and protected branches
            if [[ "$branch" != "$current_branch" && "$branch" != "main" && "$branch" != "master" ]]; then
                echo "  Deleting: $branch"
                git branch -D "$branch"
            else
                echo "  Skipping protected branch: $branch"
            fi
        done
        
        echo "Cleanup complete"
    else
        git fetch --prune
    fi
}

# Git branch -D (force delete branch)
# Usage: gbD <branch-name>
gbD() {
    if [ -z "$1" ]; then
        echo "Error: Branch name required"
        echo "Usage: gbD <branch-name>"
        return 1
    fi
    
    git branch -D "$1"
}

# Git status
# Usage: gst
gst() {
    git status
}

# Git branch all
# Usage: gba
gba() {
    echo
    git branch -a
}

# Git restore file name, fail if file not found
# Usage: grf <file-name>
gr() {
    if [ -z "$1" ]; then
        echo "Error: File name required"
        echo "Usage: gr <file-name>"
        return 1
    fi
    
    git restore "$1"
}
