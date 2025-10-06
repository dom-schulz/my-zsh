# WSL Installation Guide

Quick guide for setting up my-zsh on Windows Subsystem for Linux (WSL).

## Prerequisites

Make sure zsh is installed:
```bash
sudo apt update
sudo apt install zsh -y
```

## Installation Steps

### 1. Clone and Setup

From your current shell (bash is fine):

```bash
# Clone the repository
cd ~
git clone <your-repo-url> my-zsh

# Navigate to the directory
cd my-zsh

# Make setup script executable and run it
chmod +x setup.sh
./setup.sh
```

The setup script will configure your `~/.zshrc` file.

### 2. Switch to ZSH

You have two options:

#### Option A: Start ZSH Now (Temporary)
Just type:
```bash
zsh
```

You'll see your new prompt! But this only lasts for this session.

#### Option B: Make ZSH Your Default Shell (Recommended)
```bash
chsh -s $(which zsh)
```

Then **restart your terminal** or WSL session. ZSH will now be your default shell.

## Verification

After switching to zsh, you should see:
- A clean, colorful prompt
- Repository information when in git directories
- The `❯` prompt symbol

Test your git functions:
```bash
gst              # Should run git status
gfo              # Should fetch from origin
```

## Troubleshooting

### "Command 'setopt' not found"
You're trying to source .zshrc from bash. Instead, just type `zsh` to switch shells.

### "Command not found" errors after switching to zsh
Run the setup script again:
```bash
cd ~/my-zsh
./setup.sh
```

### Prompt doesn't look right
Make sure your terminal supports UTF-8 and has a font with emoji support:
- Windows Terminal (recommended)
- VS Code integrated terminal
- Install a Nerd Font if needed

### Want to go back to bash?
```bash
chsh -s $(which bash)
```
Then restart your terminal.

## WSL-Specific Tips

### Opening WSL in Windows Terminal
Windows Terminal should automatically detect your WSL installation. If you've set zsh as default, it will start with zsh.

### Accessing Windows Files
Your Windows drives are mounted at `/mnt/`:
```bash
cd /mnt/c/Users/YourUsername/Documents
```

### Performance
For best performance, keep your projects in your WSL home directory (`~`) rather than in `/mnt/c/`.

## Quick Reference

Once setup is complete:

```bash
# Start zsh (if not default)
zsh

# Update configuration after changes
cd ~/my-zsh
./setup.sh
source ~/.zshrc

# Test git functions
gacmp "test commit"  # Add, commit, push
gco main             # Checkout main
gfp                  # Fetch prune
```

## Making It Permanent

To ensure zsh starts automatically in Windows Terminal:
1. Open Windows Terminal Settings (Ctrl + ,)
2. Find your WSL profile
3. In "Command line" field, append ` -c zsh`:
   ```
   wsl.exe -d Ubuntu -c zsh
   ```
4. Save

Alternatively, just set zsh as default with `chsh -s $(which zsh)` and restart WSL.

