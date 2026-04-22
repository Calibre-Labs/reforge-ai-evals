#!/bin/bash
# Install all Claude Code skills from this repo into ~/.claude/commands/
# Run from the repo root: bash install-skills.sh

set -e

COMMANDS_DIR="$HOME/.claude/commands"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
MCP_DIR="$SCRIPT_DIR/mcp"

echo "Installing skills to $COMMANDS_DIR..."
mkdir -p "$COMMANDS_DIR"

for skill_file in "$SKILLS_DIR"/*-skill.md; do
    name=$(basename "$skill_file" -skill.md)
    cp "$skill_file" "$COMMANDS_DIR/$name.md"
    echo "  ✓ /$name"
done

echo ""
echo "All skills installed. They are available as slash commands in any Claude Code session."
echo ""

# MCP server setup
echo "----"
echo "Optional: braintrust-write MCP server (enables native dataset writes from Claude)"
echo ""
echo "1. Install dependencies:"
echo "   pip install -r $MCP_DIR/requirements.txt"
echo ""
echo "2. Set your API key:"
echo "   export BRAINTRUST_API_KEY=your_key_here"
echo ""
echo "3. Add to ~/.claude/settings.json under mcpServers:"
cat <<EOF
   {
     "mcpServers": {
       "braintrust-write": {
         "command": "python",
         "args": ["$MCP_DIR/server.py"],
         "env": {
           "BRAINTRUST_API_KEY": "\${BRAINTRUST_API_KEY}"
         }
       }
     }
   }
EOF
echo ""
echo "After adding, restart Claude Code and the insert_dataset_row tool will be available."
