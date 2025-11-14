#!/usr/bin/env python3
"""Progressive tool discovery utilities for context-efficient MCP usage."""

import ast
from pathlib import Path
from typing import Literal


def discover_tools(mcp_tools_path: str) -> list[str]:
    """
    List available MCP servers.
    
    Args:
        mcp_tools_path: Path to generated MCP tools directory
        
    Returns:
        List of server names
    """
    path = Path(mcp_tools_path)
    return [d.name for d in path.iterdir() if d.is_dir() and not d.name.startswith("_")]


def list_server_tools(mcp_tools_path: str, server: str) -> list[str]:
    """
    List tools available in a server.
    
    Args:
        mcp_tools_path: Path to generated MCP tools directory
        server: Server name
        
    Returns:
        List of tool names (without .py extension)
    """
    server_path = Path(mcp_tools_path) / server
    return [
        f.stem for f in server_path.glob("*.py") 
        if f.stem not in ("__init__", "client")
    ]


def load_tool_definition(
    tool_path: str, 
    detail: Literal["name_only", "signature", "full"] = "signature"
) -> dict[str, str]:
    """
    Load tool definition with configurable detail level.
    
    Args:
        tool_path: Path to tool .py file
        detail: Level of detail to return
            - name_only: Just the function name
            - signature: Name + parameters
            - full: Complete code including docstring
            
    Returns:
        Dictionary with tool information
    """
    path = Path(tool_path)
    
    if detail == "name_only":
        return {"name": path.stem, "path": str(path)}
    
    # Parse the file
    with open(path) as f:
        code = f.read()
    
    tree = ast.parse(code)
    
    # Find the main async function
    func = next((node for node in tree.body if isinstance(node, ast.AsyncFunctionDef)), None)
    
    if not func:
        return {"name": path.stem, "path": str(path)}
    
    # Extract signature
    params = [arg.arg for arg in func.args.args]
    signature = f"{func.name}({', '.join(params)})"
    
    if detail == "signature":
        docstring = ast.get_docstring(func, clean=True) or ""
        return {
            "name": func.name,
            "signature": signature,
            "description": docstring.split("\n")[0] if docstring else "",
            "path": str(path),
        }
    
    # detail == "full"
    return {
        "name": func.name,
        "signature": signature,
        "code": code,
        "path": str(path),
    }


def search_tools(
    mcp_tools_path: str,
    query: str,
    detail: Literal["name_only", "signature", "full"] = "signature"
) -> list[dict[str, str]]:
    """
    Search for tools matching a query.
    
    Args:
        mcp_tools_path: Path to generated MCP tools directory
        query: Search query (matches server name, tool name, or description)
        detail: Level of detail to return
        
    Returns:
        List of matching tool definitions
    """
    results = []
    query_lower = query.lower()
    
    for server in discover_tools(mcp_tools_path):
        if query_lower in server.lower():
            # Server name matches, include all tools
            for tool in list_server_tools(mcp_tools_path, server):
                tool_path = f"{mcp_tools_path}/{server}/{tool}.py"
                results.append(load_tool_definition(tool_path, detail))
        else:
            # Check individual tools
            for tool in list_server_tools(mcp_tools_path, server):
                if query_lower in tool.lower():
                    tool_path = f"{mcp_tools_path}/{server}/{tool}.py"
                    results.append(load_tool_definition(tool_path, detail))
    
    return results


# Multi-agent coordinator functions

async def discovery_agent(mcp_tools_path: str, task_description: str) -> list[str]:
    """
    Agent that identifies relevant tools for a task.
    Returns list of tool paths to load.
    
    Context cost: Minimal (only task description + tool names)
    """
    # Extract keywords from task
    keywords = task_description.lower().split()
    
    relevant_tools = []
    for keyword in keywords:
        matches = search_tools(mcp_tools_path, keyword, detail="name_only")
        relevant_tools.extend(match["path"] for match in matches)
    
    return list(set(relevant_tools))  # Deduplicate


async def execution_agent(tool_paths: list[str], task_description: str) -> str:
    """
    Agent that writes context-efficient code using identified tools.
    Only loads the specific tool definitions needed.
    
    Context cost: Task + selected tool definitions only
    """
    # Load only the needed tool definitions
    tools = [load_tool_definition(path, detail="full") for path in tool_paths]
    
    # This would generate code using an LLM with minimal context
    # For now, return a template
    return f"# Code using {len(tools)} tools for: {task_description}\n# {tool_paths}"


async def filtering_agent(execution_result: dict, user_query: str) -> dict:
    """
    Agent that processes raw results and returns only relevant data.
    Runs in execution environment, only returns filtered output.
    
    Context cost: Only final filtered results
    """
    # Example: Filter large dataset to only relevant rows
    if isinstance(execution_result, list):
        # Return summary instead of full data
        return {
            "count": len(execution_result),
            "sample": execution_result[:3] if execution_result else [],
        }
    
    return execution_result
