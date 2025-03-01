#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    # Export all variables from .env
    set -a
    source .env
    set +a
else
    echo "Warning: .env file not found"
fi

# Now you can use variables from .env
VENV_PATH="${VIRTUAL_ENV:-/~/.venv}"
BRANCH="${GIT_BRANCH:-main}"
TIMESTAMP=$(date +%s)

# Function to log messages
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Git operations with environment variables
git_update() {
    local commit_message="${COMMIT_PREFIX:-Update} ($TIMESTAMP)"

    # Add all changes
    git add .

    # Commit with timestamp
    git commit -m "$commit_message"

    # Push to specified branch
    git push origin "${BRANCH}"
}

# Execute Python script with virtual environment
"${VENV_PATH}/bin/python" ./clean_requirements.py

# Execute git operations
git_update
