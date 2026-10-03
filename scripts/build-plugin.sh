#!/bin/bash
# Package the plugin as dist/calibre-evals.plugin for the Claude desktop app.
# Run from the repo root: bash scripts/build-plugin.sh
set -e
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p dist
rm -f dist/calibre-evals.plugin
zip -r dist/calibre-evals.plugin .claude-plugin skills README.md -x "*.DS_Store" > /dev/null
echo "Wrote dist/calibre-evals.plugin"
