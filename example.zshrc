# ============================================================
# Example .zshrc Configuration with Git Branch Autocompletion
# Copy this to your ~/.zshrc or use as a reference
# ============================================================

# ============================================================
# ZSH COMPLETION SETUP (Must come BEFORE my-zsh configuration)
# ============================================================

# Add Homebrew git completion directory to fpath
# Choose based on your Mac architecture:

# Apple Silicon (M1/M2/M3):
fpath=(/opt/homebrew/share/zsh/site-functions $fpath)

# Intel Mac (uncomment this line instead if on Intel):
# fpath=(/usr/local/share/zsh/site-functions $fpath)

# Initialize the completion system
autoload -Uz compinit
compinit -i

# Quality-of-life completion settings (optional but recommended)
setopt completeinword                    # Complete from both ends of word
zstyle ':completion:*' menu select       # Enable visual menu selection
zstyle ':completion:*:git-*:*' tag-order 'commands' 'aliases' 'branches' 'remotes' 'tags'

# Additional completion enhancements (optional)
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'  # Case-insensitive completion
zstyle ':completion:*' list-colors ''                    # Colorize completion lists
zstyle ':completion:*:descriptions' format '%U%B%d%b%u'  # Format completion group descriptions
zstyle ':completion:*:warnings' format '%BSorry, no matches for: %d%b'

# ============================================================
# MY-ZSH CONFIGURATION
# ============================================================

# >>> my-zsh configuration >>>
MY_ZSH_DIR="$HOME/my-zsh"

# Load your chosen theme (refined or simple)
source "$MY_ZSH_DIR/themes/refined.zsh-theme"
# source "$MY_ZSH_DIR/themes/simple.zsh-theme"  # Alternative

# Load all function files (includes git functions and completions)
for func_file in "$MY_ZSH_DIR/functions"/*.zsh; do
    [ -f "$func_file" ] && source "$func_file"
done

# Common aliases
alias ll='ls -lah'
alias la='ls -A'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Git aliases (in addition to custom functions)
alias gs='git status'
alias gd='git diff'
alias gl='git log --oneline --graph --decorate --all'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gpl='git pull'

# Docker aliases (if you use Docker)
alias dps='docker ps'
alias dpa='docker ps -a'
alias di='docker images'

# System aliases
alias reload='source ~/.zshrc'
alias zshconfig='code ~/.zshrc'  # Or use your preferred editor

# <<< my-zsh configuration <<<

# ============================================================
# YOUR CUSTOM CONFIGURATION
# Add your personal settings below
# ============================================================

# Example: Set default editor
export EDITOR='vim'

# Example: Add custom bin directory to PATH
# export PATH="$HOME/bin:$PATH"

# Example: Node version manager
# export NVM_DIR="$HOME/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Example: Python virtual environment
# source ~/venv/bin/activate

# Example: Custom functions
# myfunction() {
#     echo "Hello from custom function"
# }

