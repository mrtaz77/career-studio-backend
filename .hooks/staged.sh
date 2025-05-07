#!/bin/bash
set -e

# Save unstaged changes
git stash -k -u -m "pre-commit-untracked"

# Get list of staged Python files
FILES=$(git diff --name-only --cached -- '*.py')
if [ -n "$FILES" ]; then
    echo "Formatting staged Python files..."
    black $FILES
    isort $FILES
    git add $FILES
fi

# Restore unstaged changes
STASHES=$(git stash list)
if echo "$STASHES" | grep -q "pre-commit-untracked"; then
    git stash pop
fi
