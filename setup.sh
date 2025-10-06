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

# Check if zsh is installed
if ! command -v zsh &> /dev/null; then
    echo -e "${YELLOW}⚠️  ZSH is not installed. Attempting to install...${NC}\n"
    
    # Detect OS and package manager
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            echo -e "${BLUE}📦 Detected apt package manager (Debian/Ubuntu)${NC}"
            sudo apt-get update
            sudo apt-get install -y zsh
        elif command -v yum &> /dev/null; then
            echo -e "${BLUE}📦 Detected yum package manager (RHEL/CentOS)${NC}"
            sudo yum install -y zsh
        elif command -v dnf &> /dev/null; then
            echo -e "${BLUE}📦 Detected dnf package manager (Fedora)${NC}"
            sudo dnf install -y zsh
        elif command -v pacman &> /dev/null; then
            echo -e "${BLUE}📦 Detected pacman package manager (Arch)${NC}"
            sudo pacman -S --noconfirm zsh
        else
            echo -e "${RED}❌ Could not detect package manager. Please install zsh manually:${NC}"
            echo -e "   Ubuntu/Debian: ${GREEN}sudo apt-get install zsh${NC}"
            echo -e "   RHEL/CentOS:   ${GREEN}sudo yum install zsh${NC}"
            echo -e "   Fedora:        ${GREEN}sudo dnf install zsh${NC}"
            echo -e "   Arch:          ${GREEN}sudo pacman -S zsh${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo -e "${BLUE}📦 Detected Homebrew (macOS)${NC}"
            brew install zsh
        else
            echo -e "${YELLOW}⚠️  Homebrew not found. Install it from: https://brew.sh${NC}"
            echo -e "${YELLOW}   Then run: ${GREEN}brew install zsh${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Unsupported operating system: $OSTYPE${NC}"
        echo -e "   Please install zsh manually and re-run this script."
        exit 1
    fi
    
    # Verify installation
    if command -v zsh &> /dev/null; then
        echo -e "${GREEN}✅ ZSH installed successfully!${NC}\n"
    else
        echo -e "${RED}❌ ZSH installation failed. Please install manually.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ ZSH is already installed${NC}"
    echo -e "   Version: $(zsh --version)\n"
fi

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
echo -e "  - ZSH is installed and ready"
echo -e "  - Backed up your previous .zshrc (if it existed)"
echo -e "  - Added refined theme from: ${SCRIPT_DIR}/themes/"
echo -e "  - Loaded custom functions from: ${SCRIPT_DIR}/functions/"
echo -e ""
echo -e "${YELLOW}⚡ To start using your new setup:${NC}"
echo -e "  ${GREEN}zsh${NC}"
echo -e ""
echo -e "${BLUE}💡 To make ZSH your default shell:${NC}"
echo -e "  ${GREEN}chsh -s \$(which zsh)${NC}"
echo -e "  Then restart your terminal"
echo -e ""
echo -e "${BLUE}📝 Tips:${NC}"
echo -e "  - Add your custom functions to: ${SCRIPT_DIR}/functions/"
echo -e "  - Edit the theme in: ${SCRIPT_DIR}/themes/refined.zsh-theme"
echo -e "  - Re-run this script anytime to update your configuration"
echo -e ""

