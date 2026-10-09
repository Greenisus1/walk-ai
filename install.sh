#!/bin/sh
set -eu
wget -O walk_ai.py https://raw.githubusercontent.com/Greenisus1/walk-ai/4446fc3d621aca2fbf1a92f5452f887460bdef03/walk_ai.py
exec python3 walk_ai.py "$@"
