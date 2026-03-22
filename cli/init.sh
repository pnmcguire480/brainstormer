#!/usr/bin/env bash
# BrainStormer CLI wrapper for Unix systems
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/brainstormer.py" "$@"
