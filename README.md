# My ZSH Configuration

A portable ZSH configuration setup with the refined theme and custom functions. Simply clone and run the setup script on any new machine.

## Features

- **Refined Theme**: Clean and minimal prompt with git status integration
- **Custom Functions**: Extensible function library for common tasks
- **Easy Setup**: One-command installation on new machines
- **Safe Updates**: Automatic backup of existing configuration

## Quick Start

### Prerequisites

- Git for cloning the repository
- ZSH will be automatically installed by the setup script if not present

### Installation

1. Clone this repository:
```bash
git clone <your-repo-url> ~/my-zsh
cd ~/my-zsh
```

2. Run the setup script (will auto-install zsh if needed):
```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- ✅ Detect your OS and install zsh if not present
- ✅ Backup your existing `.zshrc`
- ✅ Configure the refined theme
- ✅ Load all custom functions

3. **Switch to zsh** (if not already using it):
```bash
zsh
```

The configuration will automatically load! To make zsh your default shell:
```bash
chsh -s $(which zsh)
```
Then restart your terminal.

## What's Included

### Refined Theme
A beautiful, minimal theme (based on Pure by Sindre Sorhus) featuring:
- **Repository information**: Shows repo name, current path, and VCS branch
- **Git status indicators**: 
  - `*` for dirty/modified files
  - `!` for unstaged changes
  - `+` for staged changes
- **Command execution time**: Displays execution time for commands that take >5 seconds
- **Smart prompt**: 
  - Magenta `❯` on success
  - Red `❯` on command failure
- **SSH detection**: Shows `user@host` when connected via SSH
- **Multi-VCS support**: Works with Git, Mercurial (hg), and Bazaar (bzr)

### Custom Functions

#### `mkcd <directory>`
Create a directory and immediately cd into it.

#### `extract <file>`
Universal extraction function supporting:
- tar.gz, tar.bz2, zip, rar, 7z, and more

#### `ff <pattern>`
Find files by name pattern recursively.

#### `serve [port]`
Start a simple HTTP server (default port: 8000).

#### Git Workflow Functions

**Commit & Push:**
- `gacmp "message"` - Add all, commit, and push to current branch (complete workflow)
- `gacm "message"` - Add all and commit with message

**Branch Operations:**
- `gco <branch>` - Checkout existing branch
- `gcob <branch>` - Create and checkout new branch
- `gbD <branch>` - Force delete branch (fails if no branch name provided)

**Remote Operations:**
- `gfo` - Fetch from origin
- `gp` - Git pull
- `gfp` - Fetch with prune (removes deleted remote branches)

**Reset Operations:**
- `grho <branch>` - Reset hard to origin/branch (⚠️ with confirmation prompt)

**Quick Status:**
- `gst` - Git status

### Aliases

- `ll` - detailed list view with hidden files
- `..` - go up one directory
- `...` - go up two directories
- `gs` - git status
- `gd` - git diff
- `gl` - pretty git log

## Customization

### Adding Your Own Functions

Create new `.zsh` files in the `functions/` directory:

```bash
echo 'myfunction() { echo "Hello World"; }' > functions/my-custom.zsh
```

All `.zsh` files in the functions directory are automatically loaded.

### Modifying the Theme

Edit `themes/refined.zsh-theme` to customize:
- Prompt symbols
- Colors
- Git status indicators
- Layout and formatting

### Adding More Aliases

Edit the aliases section in your `~/.zshrc` under the my-zsh configuration block, or add them directly in a function file.

## Directory Structure

```
my-zsh/
├── README.md                      # This file
├── setup.sh                       # Installation script (Unix/Linux/macOS/WSL)
├── setup.ps1                      # Installation script (Windows PowerShell)
├── .gitignore                     # Git ignore rules
├── themes/
│   └── refined.zsh-theme         # Refined theme (Pure-based)
└── functions/
    ├── example-functions.zsh     # Utility functions
    └── git-functions.zsh         # Git workflow functions
```

## Git Function Examples

### Quick Workflow
```bash
# Make changes, then commit and push in one command
gacmp "Add user authentication feature"

# Create a new feature branch
gcob feature/new-dashboard

# Switch to existing branch
gco main

# Fetch latest and prune deleted branches
gfp

# Reset your branch to match origin (with confirmation)
grho main
```

### Complete Feature Workflow
```bash
# Create feature branch
gcob feature/user-profile

# ... make changes ...

# Commit and push
gacmp "Implement user profile page"

# Switch back to main
gco main

# Pull latest
gp

# Delete feature branch after merge
gbD feature/user-profile
```

## Updating Configuration

To update your configuration after making changes:

1. Edit files in this repository
2. Re-run the setup script:
```bash
./setup.sh
```
3. Reload your shell:
```bash
source ~/.zshrc
```

## Uninstallation

To remove the configuration:

1. Edit `~/.zshrc` and remove the section between:
```bash
# >>> my-zsh configuration >>>
# ... 
# <<< my-zsh configuration <<<
```

2. Restore from backup if needed:
```bash
cp ~/.zshrc.backup.YYYYMMDD_HHMMSS ~/.zshrc
```

## Compatibility

- Requires ZSH (tested on 5.0+)
- Works on Linux, macOS, and WSL
- Git integration requires git to be installed

## Contributing

Feel free to add your own functions and improvements!

## License

Free to use and modify for personal use.

