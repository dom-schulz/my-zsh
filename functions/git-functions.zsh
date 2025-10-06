# Git utility functions
# Shortcuts for common git workflows

# Git add, commit, and push with message
# Usage: gacmp "commit message"
gacmp() {
    if [ -z "$1" ]; then
        echo "❌ Error: Commit message required"
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
        echo "❌ Error: Commit message required"
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
        echo "❌ Error: Branch name required"
        echo "Usage: grho <branch-name>"
        return 1
    fi
    
    echo "⚠️  This will reset hard to origin/$1"
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
        echo "❌ Error: Branch name required"
        echo "Usage: gco <branch-name>"
        return 1
    fi
    
    git checkout "$1"
}

# Git checkout -b (create new branch)
# Usage: gcob <new-branch-name>
gcob() {
    if [ -z "$1" ]; then
        echo "❌ Error: Branch name required"
        echo "Usage: gcob <new-branch-name>"
        return 1
    fi
    
    git checkout -b "$1"
}

# Git fetch prune
# Usage: gfp
gfp() {
    git fetch --prune
}

# Git branch -D (force delete branch)
# Usage: gbD <branch-name>
gbD() {
    if [ -z "$1" ]; then
        echo "❌ Error: Branch name required"
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
    git branch -a
}
