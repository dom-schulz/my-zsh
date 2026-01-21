# ms CLI

Multi-service workspace management tool.

## Installation

```bash
# From workspace root
pip install -e ./my-zsh
```

## Shell Integration (Zsh)

Add these lines to your `~/.zshrc`:

```bash
# Initialize zsh completion system (if not already done)
autoload -Uz compinit && compinit

# ms aliases and completion
eval "$(ms aliases)"
eval "$(ms completion)"
```

Then reload your shell:

```bash
source ~/.zshrc
```

**Features:**
- **Shortcuts**: Use `<repo-alias> env ls` instead of `ms <repo-alias> env ls`
- **Tab Completion**: 
  - `gco <TAB>` - Complete branch names
  - `gco branch --repo <TAB>` - Complete repo aliases (or `-r <TAB>`)
  - `gco -r <repo-alias> <TAB>` - Complete branches only from the specified repo
  - Works with all git commands (gst, gco, gfo, gpu, gcob, gba, ga, gcm, gp, gfp, gd)

**Git Commands:**
- `gst` - Git status
- `gco <branch>` - Git checkout
- `gfo` - Git fetch origin
- `gpu` - Git pull
- `gcob <branch>` - Git checkout -b (create new branch)
- `gba` - Git branch -a (list all branches)
- `ga` - Git add .
- `gcm <message>` - Git commit -m
- `gp` - Git push
- `gfp --force` - Git fetch --prune and delete gone branches
- `gd` - Git diff

## Usage

- **Setup**: `ms setup`
- **List Env**: `ms <repo_alias> env ls` (or `<repo-alias> env ls` if integrated)
- **Modify Env**: `ms <repo_alias> env set <KEY>` (or `<repo-alias> env set <KEY>` if integrated)
