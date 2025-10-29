# My ZSH Configuration

A portable ZSH configuration setup with the refined theme and custom functions. Simply clone and run the setup script on any new machine.

## Features

- **Two Themes**: Choose between refined (feature-rich) or simple (compact)
  - Auto-recommends based on SSH detection (simple for remote, refined for local)
- **Custom Functions**: Extensible function library for common tasks
- **🎯 Git Branch Autocompletion**: Tab completion for branch names in all git functions
- **Easy Setup**: One-command installation on new machines
- **Safe Updates**: Automatic backup of existing configuration

## Quick Start

### Prerequisites

- Git for cloning the repository
- ZSH will be automatically installed by the setup script if not present
- For Git branch autocompletion: Homebrew's git (includes completion files)

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
- ✅ **Prompt you to select a theme** (with smart recommendations)
- ✅ Backup your existing `.zshrc`
- ✅ Configure your chosen theme
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

### Themes

You'll be prompted to choose during setup. The script automatically recommends:
- **Simple** for SSH/remote sessions
- **Refined** for local development

#### Refined Theme (Recommended for Local Dev)
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

**Example:**
```
my-zsh/themes git:main* 12s

❯ 
```

#### Simple Theme (Recommended for SSH/Remote)
A clean, compact single-line theme (based on geoffgarside) featuring:
- **Hostname display**: Red hostname (perfect for identifying remote servers)
- **Current directory**: Green directory name
- **Git branch**: Blue git branch in parentheses
- **Compact format**: Everything on one line, minimal resource usage

**Example:**
```
server-name:my-zsh (main) $ 
```

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

**All branch operation functions support tab autocompletion for branch names!**

**Commit & Push:**
- `gacmp "message"` - Add all, commit, and push to current branch (complete workflow)
- `gacm "message"` - Add all and commit with message

**Branch Operations:**
- `gco <branch>` - Checkout existing branch (✨ autocompletes local & remote branches)
- `gcob <branch>` - Create and checkout new branch
- `gbD <branch>` - Force delete branch (✨ autocompletes local branches)

**Remote Operations:**
- `gfo` - Fetch from origin
- `gp` - Git pull
- `gfp` - Fetch with prune (removes deleted remote branches)

**Reset Operations:**
- `grho <branch>` - Reset hard to origin/branch (✨ autocompletes remote branches, ⚠️ with confirmation prompt)

**File Operations:**
- `gr <file>` - Git restore file (✨ autocompletes modified files)

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

### Enabling Git Branch Autocompletion ⚡

Enable intelligent tab completion for branch names! Just add this to your `~/.zshrc` **before** the my-zsh configuration:

```bash
# Apple Silicon:
fpath=(/opt/homebrew/share/zsh/site-functions $fpath)
# Intel Mac: use /usr/local/share/zsh/site-functions instead

autoload -Uz compinit
compinit -i

setopt completeinword
zstyle ':completion:*' menu select
```

Then reload: `source ~/.zshrc`

**Test it:** Type `gco <TAB>` and see your branches!

📚 **Detailed guides:**
- **Quick Start**: See `QUICKSTART_AUTOCOMPLETION.md` (3 simple steps)
- **Full Guide**: See `AUTOCOMPLETION_SETUP.md` (complete setup + troubleshooting)
- **Example Config**: See `example.zshrc` (ready-to-use template)

**What gets autocompletion:**
- `gco <TAB>` - All branches (local + remote)
- `grho <TAB>` - Remote branches
- `gbD <TAB>` - Local branches
- `gr <TAB>` - Modified files

### Switching Themes

To change themes, simply re-run the setup script:
```bash
cd ~/my-zsh
./setup.sh
```

You'll be prompted to select a theme again.

### Modifying Themes

Edit the theme files to customize:
- `themes/refined.zsh-theme` - Feature-rich theme
- `themes/simple.zsh-theme` - Compact theme

Customize:
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
├── INSTALL_WSL.md                # WSL-specific installation guide
├── .gitignore                     # Git ignore rules
├── themes/
│   ├── refined.zsh-theme         # Refined theme (Pure-based, local dev)
│   └── simple.zsh-theme          # Simple theme (compact, for SSH/remote)
└── functions/
    ├── git.zsh                   # Git workflow functions
    ├── terraform.zsh             # Terraform utility functions
    └── _git_completions.zsh      # Branch name autocompletion for git functions
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

