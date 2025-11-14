---
name: mcp-code-execution
description: Context-efficient MCP integration using code execution patterns. Use when building agents that interact with MCP servers, need to manage large tool sets (50+ tools), process large datasets through tools, or require multi-step workflows with intermediate results. Enables progressive tool loading, data filtering before context, and reusable skill persistence.
---

# MCP Code Execution

Implement context-efficient MCP integrations using code execution patterns instead of direct tool calls.

## Core Concept

Present MCP servers as code APIs on a filesystem. Load tool definitions on-demand, process data in execution environment, only return filtered results to context.

## Quick Start

### 1. Generate Tool API from MCP Server

```bash
python scripts/mcp_generator.py --server-config servers.json --output ./mcp_tools
```

Creates:
```
mcp_tools/
├── google_drive/
│   ├── get_document.py
│   └── list_files.py
├── salesforce/
│   ├── update_record.py
│   └── query.py
└── client.py  # MCP client wrapper
```

### 2. Discover Tools Progressively

```python
from scripts.tool_discovery import discover_tools, load_tool_definition

# List available servers
servers = discover_tools("./mcp_tools")
# ['google_drive', 'salesforce']

# Load only needed tool definitions
tool = load_tool_definition("./mcp_tools/google_drive/get_document.py")
```

### 3. Use Context-Efficient Patterns

```python
import mcp_tools.google_drive as gdrive
import mcp_tools.salesforce as sf

# Filter data before returning to context
sheet = await gdrive.get_sheet("abc123")
pending = [r for r in sheet if r["Status"] == "pending"]
print(f"Found {len(pending)} pending orders")  # Only summary in context

# Chain operations without intermediate context pollution
doc = await gdrive.get_document("xyz789")
await sf.update_record("Lead", "00Q123", {"Notes": doc["content"]})
print("Document attached to lead")  # Only confirmation in context
```

## Multi-Agent Workflow

For complex tasks, delegate to specialized sub-agents:

1. **Discovery Agent**: Explores available tools, returns relevant paths
2. **Execution Agent**: Writes and runs context-efficient code
3. **Filtering Agent**: Processes results, returns minimal context

See `references/patterns.md` for implementation details.

## Tool Discovery Strategies

### Filesystem Exploration
List `./mcp_tools/` directory, read specific tool files as needed.

### Search-Based Discovery
```python
from scripts.tool_discovery import search_tools

tools = search_tools("./mcp_tools", query="salesforce lead", detail="name_only")
# Returns: ['salesforce/query.py', 'salesforce/update_record.py']
```

### Lazy Loading
Only read full tool definitions when about to use them.

## Context Optimization

- **Before**: 150K tokens (all tool definitions + intermediate results)
- **After**: 2K tokens (only used tools + filtered results)
- **Savings**: 98.7%

## Persisting Skills

Save working code as reusable functions:

```python
# ./skills/extract_pending_orders.py
async def extract_pending_orders(sheet_id: str):
    sheet = await gdrive.get_sheet(sheet_id)
    return [r for r in sheet if r["Status"] == "pending"]
```

## Privacy & Security

Data processed in execution environment stays there by default. Only explicitly logged/returned values enter context.

## Advanced Patterns

See `references/patterns.md` for:
- Aggregation without context bloat
- Cross-source joins
- Polling loops
- Batch operations
- Error handling
