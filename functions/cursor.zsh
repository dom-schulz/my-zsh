# Cursor IDE utility functions

# Open Cursor IDE with specified path
# Usage: cr [path]
cr() {
    if [ -z "$1" ]; then
        # No argument, open current directory
        cursor .
    else
        # Open specified path
        cursor "$1"
    fi
}

