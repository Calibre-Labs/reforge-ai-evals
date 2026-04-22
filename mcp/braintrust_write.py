#!/usr/bin/env python3
"""
braintrust-write MCP server

Exposes write tools for Braintrust datasets and prompts — the official
Braintrust MCP server is read-only, so this fills the gap.

Name resolution: all tools accept either a full Braintrust name
("Week2 Dataset 53") or a short alias defined in names.json at the repo
root ("week2"). The project_name parameter can also be omitted if
names.json defines a default project.

Usage:
  python braintrust_write.py     # runs on stdio (for Claude Code)
  BRAINTRUST_API_KEY=... python braintrust_write.py
"""

import json
import os
from pathlib import Path
from typing import Optional

import braintrust
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("braintrust-write")

# ---------------------------------------------------------------------------
# Name resolution helpers
# ---------------------------------------------------------------------------

def _load_names() -> dict:
    names_path = Path(__file__).parent.parent / "names.json"
    if names_path.exists():
        with open(names_path) as f:
            return json.load(f)
    return {}


def _resolve(short: str, category: str, names: dict) -> str:
    """Return the full Braintrust name for a short alias, or the input unchanged."""
    return names.get(category, {}).get(short, short)


def _default_project(names: dict) -> str:
    return names.get("project", "")


def _require_api_key():
    if not os.environ.get("BRAINTRUST_API_KEY"):
        raise ValueError(
            "BRAINTRUST_API_KEY environment variable is not set. "
            "Add it to the mcpServers env config in ~/.claude/settings.json."
        )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def list_names() -> str:
    """
    Show all short-name aliases defined in names.json and the Braintrust
    names they resolve to. Use this to discover valid short names before
    calling insert_dataset_row or upsert_prompt.
    """
    names = _load_names()
    if not names:
        return "names.json not found. Create one at the repo root to enable short-name aliases."

    lines = [f"Project: {names.get('project', '(not set)')}", ""]

    if names.get("datasets"):
        lines.append("Datasets:")
        for alias, full in names["datasets"].items():
            lines.append(f"  {alias:20s} → {full}")

    if names.get("prompts"):
        lines.append("")
        lines.append("Prompts:")
        for alias, slug in names["prompts"].items():
            lines.append(f"  {alias:20s} → {slug}")

    return "\n".join(lines)


@mcp.tool()
def insert_dataset_row(
    dataset_name: str,
    input: str,
    expected: str = "",
    metadata: str = "{}",
    tags: str = "[]",
    project_name: str = "",
) -> str:
    """
    Insert a single row into a Braintrust dataset.
    Creates the dataset if it does not already exist.

    Args:
        dataset_name: Full Braintrust dataset name or short alias from names.json
                      e.g. "week2" or "Week2 Dataset 53"
        input: The query or input string for this row
        expected: Optional gold-standard reference response (leave blank if unknown)
        metadata: JSON object string with dimension tags
                  e.g. '{"query_type": "direct_category", "failure_mode": "stale_entity"}'
        tags: JSON array string of tags e.g. '["regression"]'
        project_name: Braintrust project name. Defaults to names.json project if omitted.

    Returns:
        Confirmation string with the inserted row ID
    """
    _require_api_key()
    names = _load_names()

    project = project_name or _default_project(names)
    if not project:
        raise ValueError("project_name is required (or set 'project' in names.json)")

    resolved_dataset = _resolve(dataset_name, "datasets", names)

    try:
        meta = json.loads(metadata)
    except json.JSONDecodeError as e:
        raise ValueError(f"metadata must be a valid JSON object string: {e}")

    try:
        tag_list = json.loads(tags)
    except json.JSONDecodeError as e:
        raise ValueError(f"tags must be a valid JSON array string: {e}")

    dataset = braintrust.init_dataset(project=project, name=resolved_dataset)
    row_id = dataset.insert(
        input=input,
        expected=expected if expected else None,
        metadata=meta,
        tags=tag_list,
    )
    dataset.flush()

    return f"Inserted row {row_id} into {project} / {resolved_dataset}"


@mcp.tool()
def insert_dataset_rows(
    dataset_name: str,
    rows: str,
    project_name: str = "",
) -> str:
    """
    Insert multiple rows into a Braintrust dataset in a single flush.
    Use this for batch operations (e.g. seeding from a CSV).

    Args:
        dataset_name: Full Braintrust dataset name or short alias from names.json
        rows: JSON array of row objects, each with keys:
              input (required), expected, metadata, tags
              e.g. '[{"input": "CRM software", "metadata": {"query_type": "direct_category"}}]'
        project_name: Braintrust project name. Defaults to names.json project if omitted.

    Returns:
        Confirmation string with count of inserted rows
    """
    _require_api_key()
    names = _load_names()

    project = project_name or _default_project(names)
    if not project:
        raise ValueError("project_name is required (or set 'project' in names.json)")

    resolved_dataset = _resolve(dataset_name, "datasets", names)

    try:
        row_list = json.loads(rows)
    except json.JSONDecodeError as e:
        raise ValueError(f"rows must be a valid JSON array string: {e}")

    if not isinstance(row_list, list):
        raise ValueError("rows must be a JSON array")

    dataset = braintrust.init_dataset(project=project, name=resolved_dataset)

    ids = []
    for row in row_list:
        row_id = dataset.insert(
            input=row.get("input", ""),
            expected=row.get("expected") or None,
            metadata=row.get("metadata", {}),
            tags=row.get("tags", []),
        )
        ids.append(row_id)

    dataset.flush()

    return f"Inserted {len(ids)} rows into {project} / {resolved_dataset}"


@mcp.tool()
def upsert_prompt(
    prompt_name: str,
    system_prompt: str,
    model: str = "claude-sonnet-4-6",
    description: str = "",
    project_name: str = "",
) -> str:
    """
    Push a new prompt version to Braintrust. Each call creates a new version;
    Braintrust tracks the full history. Use this when iterating on a system
    prompt so every version is logged alongside its experiment results.

    Args:
        prompt_name: Short alias from names.json or a new slug for a new prompt.
                     e.g. "market_map_v2" (alias) or "market-map-v3" (new slug)
        system_prompt: The full system prompt text to store as this version.
                       Tip: read the file first with the Read tool, then pass the content here.
        model: Model this prompt is intended for. Stored as metadata.
               e.g. "claude-sonnet-4-6", "gpt-4o"
        description: Optional human-readable note about what changed in this version.
        project_name: Braintrust project name. Defaults to names.json project if omitted.

    Returns:
        Confirmation string with the prompt slug and version info.
    """
    _require_api_key()
    names = _load_names()

    project = project_name or _default_project(names)
    if not project:
        raise ValueError("project_name is required (or set 'project' in names.json)")

    resolved_slug = _resolve(prompt_name, "prompts", names)

    result = braintrust.create_prompt(
        name=resolved_slug,
        project_name=project,
        prompt={
            "messages": [{"role": "system", "content": system_prompt}]
        },
        model=model,
        description=description or None,
    )

    # Suggest updating names.json if this is a new slug not yet aliased
    existing_slugs = set(names.get("prompts", {}).values())
    hint = ""
    if resolved_slug not in existing_slugs:
        hint = f"\nTip: add '{prompt_name}: \"{resolved_slug}\"' to names.json prompts to alias it."

    return f"Created prompt version: {resolved_slug} in {project}{hint}"


if __name__ == "__main__":
    mcp.run()
