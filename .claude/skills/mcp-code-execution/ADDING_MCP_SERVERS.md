# Adding New MCP Servers (On-Demand Pattern)

This guide explains how to add new MCP servers following the on-demand loading pattern to avoid context pollution.

## Why This Approach?

**Problem with Default MCP Loading:**
- Adding MCP server to `settings.json` → all tools load into context immediately
- Example: Azure DevOps MCP has 50+ tools
- Each tool = 200-500 tokens of context
- Total waste: 10,000-25,000 tokens for tools you might never use

**Solution: On-Demand Pattern:**
- Keep MCP configs in registry, not settings
- Load only when needed via skills
- Use REST API helpers for common operations
- Filter results before returning to context
- Context savings: 95-98%

## Step-by-Step: Adding a New MCP Server

### Step 1: Add MCP Server to Registry

Edit: `/home/vscode/.claude/skills/mcp-code-execution/mcp_configs/registry.json`

```json
{
  "servers": {
    "your-server-name": {
      "name": "Your MCP Server Display Name",
      "description": "What this MCP server does",
      "command": "npx",
      "args": ["-y", "@your-package/mcp-server", "--option", "value"],
      "env": {
        "API_KEY": "${YOUR_API_KEY_ENV_VAR}",
        "OTHER_CONFIG": "${OTHER_ENV_VAR}"
      },
      "config_file": "/path/to/optional/config.json"
    }
  }
}
```

**Field Guide:**
- `name`: Human-readable name
- `description`: What operations this server provides
- `command`: Command to start the server (usually `npx` or `python`)
- `args`: Command-line arguments
- `env`: Environment variables (use `${VAR}` for env var substitution)
- `config_file`: Optional path to dedicated config file

### Step 2: Create Dedicated Skill Directory

```bash
mkdir -p /home/vscode/.claude/skills/your-server-name/scripts
```

### Step 3: Create Helper Scripts

Create: `/home/vscode/.claude/skills/your-server-name/scripts/helper.py`

**Pattern: Use REST API directly when possible**

```python
#!/usr/bin/env python3
"""Helper functions for [Your Service Name]."""
import os
import json
import requests
from typing import Any


class YourServiceHelper:
    """Context-efficient helper for [Your Service]."""

    def __init__(self):
        self.api_key = os.getenv("YOUR_API_KEY")
        if not self.api_key:
            raise ValueError("YOUR_API_KEY environment variable not set")
        self.base_url = "https://api.yourservice.com/v1"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def _get(self, endpoint: str) -> dict[str, Any]:
        """Make GET request to API."""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_resource(self, resource_id: str) -> dict[str, Any]:
        """
        Get resource by ID.

        Returns only essential fields to minimize context usage.
        """
        data = self._get(f"resources/{resource_id}")
        # Filter to only essential fields
        return {
            "id": data["id"],
            "name": data["name"],
            "status": data["status"]
            # Don't return full nested objects, metadata, etc.
        }


def main():
    """CLI interface for testing."""
    import sys
    if len(sys.argv) < 2:
        print("Usage: helper.py <resource_id>")
        sys.exit(1)
    helper = YourServiceHelper()
    result = helper.get_resource(sys.argv[1])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

**Key Principles:**
1. Use REST API directly (faster than MCP overhead)
2. Filter results to only essential data
3. Return summaries, not full objects
4. Make it CLI-friendly for testing

### Step 4: Create Skill Documentation

Create: `/home/vscode/.claude/skills/your-server-name/skill.md`

```markdown
---
name: your-server-name
description: On-demand operations for [Your Service]. Loaded only when needed to avoid context pollution.
---

# Your Service Name (On-Demand)

Context-efficient operations for [Your Service] without loading all MCP tools.

## Prerequisites

```bash
export YOUR_API_KEY="your-key"
export OTHER_CONFIG="value"
```

## Available Operations

### Operation 1

```python
from scripts.helper import YourServiceHelper

helper = YourServiceHelper()
result = helper.get_resource("resource-123")
print(result["status"])
```

### CLI Usage

```bash
python3 /home/vscode/.claude/skills/your-server-name/scripts/helper.py resource-123
```

## Context Efficiency

- Without this: 15,000+ tokens for all MCP tools
- With this: 500-2,000 tokens for actual work
- Savings: 85-95%

## Extending

Add new methods to `scripts/helper.py` following the pattern:
1. Make API call
2. Filter to essential data
3. Return summary

```

### Step 5: Test Your Helper

```bash
# Test CLI interface
python3 /home/vscode/.claude/skills/your-server-name/scripts/helper.py test-id

# Test programmatically
python3 -c "from your_server_name.scripts.helper import YourServiceHelper; h = YourServiceHelper(); print(h.get_resource('test-id'))"
```

### Step 6: Use in Claude Code

Now when you need this service, invoke the skill:

```
User: "Use the your-server-name skill to get resource 123"
```

Claude will:
1. Load only the specific helper
2. Execute the operation
3. Filter results
4. Return summary to context

## Examples of MCPs You Might Add

### 1. GitHub MCP
```json
{
  "github": {
    "name": "GitHub MCP",
    "description": "Repos, issues, PRs, actions, releases",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}"
    }
  }
}
```

### 2. Slack MCP
```json
{
  "slack": {
    "name": "Slack MCP",
    "description": "Channels, messages, users, threads",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-slack"],
    "env": {
      "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
      "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
    }
  }
}
```

### 3. Google Drive MCP
```json
{
  "gdrive": {
    "name": "Google Drive MCP",
    "description": "Files, folders, sheets, docs",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-gdrive"],
    "env": {
      "GOOGLE_APPLICATION_CREDENTIALS": "${GOOGLE_CREDS_PATH}"
    }
  }
}
```

### 4. Confluence MCP
```json
{
  "confluence": {
    "name": "Confluence MCP",
    "description": "Spaces, pages, search, content",
    "command": "npx",
    "args": ["-y", "mcp-server-confluence"],
    "env": {
      "CONFLUENCE_URL": "${CONFLUENCE_URL}",
      "CONFLUENCE_API_TOKEN": "${CONFLUENCE_TOKEN}"
    }
  }
}
```

## Advanced: When to Use Actual MCP Protocol

The REST API approach works for 80-90% of cases. Use actual MCP protocol when:

1. **Complex multi-step workflows** - MCP handles state better
2. **Real-time updates** - MCP streaming support
3. **No REST API available** - MCP is the only interface
4. **Advanced features** - Tool chaining, context windows

For these cases, see `/home/vscode/.claude/skills/mcp-code-execution/scripts/mcp_client.py`

## Workflow Summary

```
New MCP Server
    ↓
Add to registry.json
    ↓
Create skill directory
    ↓
Write REST API helper
    ↓
Document in skill.md
    ↓
Test helper script
    ↓
Invoke skill when needed
    ↓
Context-efficient operations ✅
```

## Current Registered Servers

Run this to see all available servers:

```bash
python3 /home/vscode/.claude/skills/mcp-code-execution/scripts/mcp_client.py list
```

## Questions?

- See working example: `/home/vscode/.claude/skills/azure-devops/`
- Check mcp-code-execution skill: `/home/vscode/.claude/skills/mcp-code-execution/skill.md`
- Anthropic MCP docs: https://modelcontextprotocol.io/
