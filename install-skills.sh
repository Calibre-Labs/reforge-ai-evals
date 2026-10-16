#!/bin/bash
# Install the skills as Claude Code slash commands in ~/.claude/commands/.
# This is the fallback for people who are not using the plugin. With the plugin
# installed (see README), you do not need this script.
# Run from the repo root: bash install-skills.sh

set -e

COMMANDS_DIR="$HOME/.claude/commands"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"

echo "Installing skills to $COMMANDS_DIR..."
mkdir -p "$COMMANDS_DIR"

for skill_dir in "$SKILLS_DIR"/*/; do
    name=$(basename "$skill_dir")
    if [ -f "$skill_dir/SKILL.md" ]; then
        cp "$skill_dir/SKILL.md" "$COMMANDS_DIR/$name.md"
        echo "  ✓ /$name"
    fi
done

echo ""
echo "Done. The skills are available as slash commands in any Claude Code session."
echo "Note: skills that ship reference files (eval-rubric) work best through the plugin,"
echo "which keeps those files next to the skill."
