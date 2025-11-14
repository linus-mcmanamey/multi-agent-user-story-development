#!/usr/bin/env python3
"""Generate file-based MCP tool APIs from server configurations."""

import json
import argparse
from pathlib import Path
from typing import Any


def generate_tool_file(tool: dict[str, Any], server_name: str) -> str:
    """Generate Python code for a single MCP tool."""
    tool_name = tool["name"]
    description = tool.get("description", "")
    params = tool.get("inputSchema", {}).get("properties", {})
    required = tool.get("inputSchema", {}).get("required", [])
    
    # Build parameter type hints
    param_list = []
    for name, schema in params.items():
        type_hint = {"string": "str", "integer": "int", "boolean": "bool"}.get(
            schema.get("type", "str"), "Any"
        )
        optional = "" if name in required else " | None = None"
        param_list.append(f"{name}: {type_hint}{optional}")
    
    param_str = ", ".join(param_list) if param_list else ""
    
    return f'''"""
{description}
"""
from typing import Any
from .client import call_mcp_tool


async def {tool_name}({param_str}) -> dict[str, Any]:
    """
    {description}
    """
    params = {{k: v for k, v in locals().items() if v is not None}}
    return await call_mcp_tool("{server_name}__{tool_name}", params)
'''


def generate_client() -> str:
    """Generate MCP client wrapper."""
    return '''"""MCP client wrapper for tool execution."""
import asyncio
from typing import Any


# Mock implementation - replace with actual MCP client
async def call_mcp_tool(tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    Call an MCP tool. Replace with your MCP client implementation.
    
    Args:
        tool_name: Fully qualified tool name (server__tool)
        params: Tool parameters
        
    Returns:
        Tool execution result
    """
    # TODO: Implement actual MCP client call
    print(f"Calling {tool_name} with {params}")
    return {"status": "success", "data": None}
'''


def generate_init(tools: list[str]) -> str:
    """Generate __init__.py for a server module."""
    imports = "\n".join(f"from .{tool} import {tool}" for tool in tools)
    exports = ", ".join(f'"{tool}"' for tool in tools)
    return f'''{imports}

__all__ = [{exports}]
'''


def main():
    parser = argparse.ArgumentParser(description="Generate MCP tool APIs")
    parser.add_argument("--server-config", required=True, help="JSON file with MCP server configurations")
    parser.add_argument("--output", default="./mcp_tools", help="Output directory")
    args = parser.parse_args()
    
    # Load server config
    with open(args.server_config) as f:
        config = json.load(f)
    
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate client
    (output_path / "client.py").write_text(generate_client())
    
    # Generate tools for each server
    for server_name, server_config in config.get("servers", {}).items():
        server_path = output_path / server_name
        server_path.mkdir(exist_ok=True)
        
        tool_names = []
        for tool in server_config.get("tools", []):
            tool_name = tool["name"]
            tool_names.append(tool_name)
            
            tool_code = generate_tool_file(tool, server_name)
            (server_path / f"{tool_name}.py").write_text(tool_code)
        
        # Generate __init__.py
        (server_path / "__init__.py").write_text(generate_init(tool_names))
    
    print(f"✓ Generated MCP tools in {output_path}")


if __name__ == "__main__":
    main()
