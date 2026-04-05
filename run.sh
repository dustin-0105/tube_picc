#!/bin/bash
# ------------------------------------------------------------------
# Auto-Curator Execution Script for Cron
# ------------------------------------------------------------------
# This script ensures that the cron job executes in the correct directory
# and uses the python executable from the virtual environment.
#
# Usage:
#   ./run.sh           # output to stdout
#   ./run.sh --log     # append output to cron.log

# 1. Capture the absolute path of the directory this script is in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 2. Change to the project directory
cd "$DIR"

# 3. Ensure CLI tools (nlm, node, etc.) are available in cron's limited PATH
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"

# 4. Activate the virtual environment
source venv/bin/activate

# 5. Run the main python script
run_bot() {
    echo "========================================"
    echo "Starting YouTube Curator Job at $(date)"
    echo "========================================"
    python3 main.py
    echo "Job finished at $(date)"
    echo "========================================"
    echo ""
}

if [ "$1" = "--log" ]; then
    run_bot >> "$DIR/cron.log" 2>&1
else
    run_bot
fi
