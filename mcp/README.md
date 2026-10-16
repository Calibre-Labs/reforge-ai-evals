# braintrust-write MCP server

An optional MCP server that lets a coding agent write dataset rows and prompts into [Braintrust](https://braintrust.dev). The official Braintrust MCP server is read-only. Nothing in the skills requires this; `ticket-to-eval` can use it if your datasets live in Braintrust.

```bash
pip install -r mcp/requirements.txt
python mcp/braintrust_write.py   # runs on stdio
```

[`names.json`](names.json) maps short aliases (such as `week2`) to full Braintrust project, dataset and prompt names.
