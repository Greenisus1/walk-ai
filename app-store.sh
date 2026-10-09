#!/bin/bash
# pi-app-store: 1
set -eu
cd -- "$(dirname -- "$0")"
case "${1:-}" in
  install)
    command -v python3 >/dev/null || { echo 'python3 is required'; exit 1; }
    python3 walk_ai.py --info >/dev/null
    echo 'Walk AI brain data ready. It now works offline.' ;;
  run) shift; exec python3 fullscreen.py "$@" ;;
  *) echo 'Use: bash app-store.sh install OR bash app-store.sh run'; exit 1 ;;
esac
