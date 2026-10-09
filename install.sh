#!/bin/sh
set -eu
wget -O walk_ai.py https://raw.githubusercontent.com/Greenisus1/walk-ai/main/walk_ai.py
exec python3 walk_ai.py "$@"
