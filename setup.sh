#!/bin/bash

# My ZSH Setup Script
# This script configures your ~/.zshrc with custom functions and the refined theme

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 Setting up ZSH configuration...${NC}\n"

# Backup existing .zshrc if it exists
if [ -f ~/.zshrc ]; then
    BACKUP_FILE=~/.zshrc.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${YELLOW}📋 Backing up existing .zshrc to ${BACKUP_FILE}${NC}"
    cp ~/.zshrc "$BACKUP_FILE"
fi

# Create new .zshrc or append to existing
echo -e "${GREEN}📝 Configuring .zshrc${NC}"

# Remove old my-zsh configuration if exists
if [ -f ~/.zshrc ]; then
    sed -i.tmp '/# >>> my-zsh configuration >>>/,/# <<< my-zsh configuration <<</d' ~/.zshrc
    rm -f ~/.zshrc.tmp
fi

# Add configuration block
cat >> ~/.zshrc << EOF

# >>> my-zsh configuration >>>
# Custom ZSH configuration from my-zsh repo
export MY_ZSH_PATH="${SCRIPT_DIR}"

# Load refined theme
source "\${MY_ZSH_PATH}/themes/refined.zsh-theme"

# Load all custom functions
for function_file in "\${MY_ZSH_PATH}/functions"/*.zsh; do
    [ -f "\$function_file" ] && source "\$function_file"
done

# Add your custom aliases here
alias ll='ls -lah'
alias ..='cd ..'
alias ...='cd ../..'
alias gs='git status'
alias gd='git diff'
alias gl='git log --oneline --graph --decorate'

# <<< my-zsh configuration <<<
EOF

echo -e "${GREEN}✅ Setup complete!${NC}\n"
echo -e "${BLUE}📌 Summary:${NC}"
echo -e "  - Backed up your previous .zshrc (if it existed)"
echo -e "  - Added refined theme from: ${SCRIPT_DIR}/themes/"
echo -e "  - Loaded custom functions from: ${SCRIPT_DIR}/functions/"
echo -e ""
echo -e "${YELLOW}⚡ To apply changes, run:${NC}"
echo -e "  ${GREEN}source ~/.zshrc${NC}"
echo -e ""
echo -e "${BLUE}💡 Tips:${NC}"
echo -e "  - Add your custom functions to: ${SCRIPT_DIR}/functions/"
echo -e "  - Edit the theme in: ${SCRIPT_DIR}/themes/refined.zsh-theme"
echo -e "  - Re-run this script anytime to update your configuration"
echo -e ""

