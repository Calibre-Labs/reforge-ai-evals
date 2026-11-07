# reforge-ai-evals

## Plugin versions

Claude Code and Claude desktop install this plugin from this repo and update it only when its version
changes. A merged change without a bump never reaches anyone. So every PR that changes the plugin bumps
the version exactly once.

- **Bump** when the PR changes what users get: anything under `skills/`, `templates/` or `scripts/`, or the plugin manifests. **Don't bump** for repo-only changes (`docs/`, the README, `llms.txt`, `CITATION.cff`, this file).
- **Which number** (semver):
  - patch (x.y.**Z**): fixes, wording, small tweaks to an existing skill or script
  - minor (x.**Y**.0): a new skill, script, option or behavior
  - major (**X**.0.0): a removed or renamed skill, or a change that breaks existing files, commands or workflows
- **Where**: `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`. Keep them identical.
- **If main moves first**: when another PR merges with the same or a higher version, re-bump above main before merging.

