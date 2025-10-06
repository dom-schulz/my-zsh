# simple.zsh-theme
# Copied and modified from the oh-my-zsh theme from geoffgarside
# Perfect for SSH sessions and remote servers
# Red server name, green cwd, blue git status

# Load colors
autoload -U colors && colors

# Enable prompt substitution
setopt PROMPT_SUBST

# Git prompt function (standalone, no oh-my-zsh required)
git_prompt_info() {
    # Check if we're in a git repo
    git rev-parse --git-dir > /dev/null 2>&1 || return
    
    # Get the current branch
    local branch=$(git symbolic-ref --short HEAD 2>/dev/null || git describe --tags --exact-match 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
    
    # Return formatted branch
    if [ -n "$branch" ]; then
        echo " %{$fg[blue]%}($branch)%{$reset_color%}"
    fi
}

PROMPT='%{$fg[red]%}%m%{$reset_color%}:%{$fg[green]%}%c%{$reset_color%}$(git_prompt_info) %(!.#.$) '

