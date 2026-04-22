#!/usr/bin/env python3
"""
braintrust-write MCP server

Exposes a write tool for Braintrust datasets — the official Braintrust MCP
server is read-only, so this fills the gap for eval workflows that need to
insert rows (e.g. ticket-to-eval skill, batch dataset seeding).

Usage:
  python server.py          # runs on stdio (for Claude Code)
  BRAINTRUST_API_KEY=... python server.py
"""

import json
import os
import sys
from typing import Optional

import braintrust
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("braintrust-write")


@mcp.tool()
def insert_dataset_row(
    project_name: str,
    dataset_name: str,
    input: str,
    expected: str = "",
    metadata: str = "{}",
    tags: str = "[]",
) -> str:
    """
    Insert a single row into a Braintrust dataset.
    Creates the dataset if it does not already exist.

    Args:
        project_name: Braintrust project name (e.g. "market-map-agent")
        dataset_name: Dataset name (e.g. "regression-dataset")
        input: The query or input string for this row
        expected: Optional gold-standard reference response (leave blank if unknown)
        metadata: JSON object string with dimension tags
                  e.g. '{"query_type": "direct_category", "failure_mode": "stale_entity"}'
        tags: JSON array string of tags e.g. '["regression"]'

    Returns:
        Confirmation string with the inserted row ID
    """
    api_key = os.environ.get("BRAINTRUST_API_KEY")
    if not api_key:
        raise ValueError(
            "BRAINTRUST_API_KEY environment variable is not set. "
            "Add it to the mcpServers env config in ~/.claude/settings.json."
        )

    try:
        meta = json.loads(metadata)
    except json.JSONDecodeError as e:
        raise ValueError(f"metadata must be a valid JSON object string: {e}")

    try:
        tag_list = json.loads(tags)
    except json.JSONDecodeError as e:
        raise ValueError(f"tags must be a valid JSON array string: {e}")

    dataset = braintrust.init_dataset(project=project_name, name=dataset_name)
    row_id = dataset.insert(
        input=input,
        expected=expected if expected else None,
        metadata=meta,
        tags=tag_list,
    )
    dataset.flush()

    return f"Inserted row {row_id} into {project_name} / {dataset_name}"


@mcp.tool()
def insert_dataset_rows(
    project_name: str,
    dataset_name: str,
    rows: str,
) -> str:
    """
    Insert multiple rows into a Braintrust dataset in a single flush.
    Use this for batch operations (e.g. seeding from a CSV).

    Args:
        project_name: Braintrust project name
        dataset_name: Dataset name
        rows: JSON array of row objects, each with keys:
              input (required), expected, metadata, tags
              e.g. '[{"input": "CRM software", "metadata": {"query_type": "direct_category"}}]'

    Returns:
        Confirmation string with count of inserted rows
    """
    api_key = os.environ.get("BRAINTRUST_API_KEY")
    if not api_key:
        raise ValueError("BRAINTRUST_API_KEY environment variable is not set.")

    try:
        row_list = json.loads(rows)
    except json.JSONDecodeError as e:
        raise ValueError(f"rows must be a valid JSON array string: {e}")

    if not isinstance(row_list, list):
        raise ValueError("rows must be a JSON array")

    dataset = braintrust.init_dataset(project=project_name, name=dataset_name)

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

    return f"Inserted {len(ids)} rows into {project_name} / {dataset_name}"


if __name__ == "__main__":
    mcp.run()
