#!/bin/bash
# ------------------------------------------------------------------
# Auto-Curator Execution Script for Cron
# ------------------------------------------------------------------
# This script ensures that the cron job executes in the correct directory
# and uses the python executable from the virtual environment.

# 1. Capture the absolute path of the directory this script is in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 2. Change to the project directory
cd "$DIR"

# 3. Output a timestamp to track execution in logs
echo "========================================"
echo "Starting YouTube Curator Job at $(date)"
echo "========================================"

# 4. Activate the virtual environment
source venv/bin/activate

# 5. Run the main python script
python3 main.py

echo "Job finished at $(date)"
echo "========================================"
