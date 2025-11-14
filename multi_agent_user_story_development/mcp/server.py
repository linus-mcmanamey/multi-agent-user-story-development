#!/usr/bin/env python3
"""MCP Server for Business Analyst and PySpark Engineer Memory Tools. Provides custom MCP tools for managing documentation, notebooks, and memory storage. Note: Schema queries now use mcp-server-motherduck directly via mcp__mcp-server-motherduck__query."""

import sys
from typing import Any

from loguru import logger

from multi_agent_user_story_development.mcp.tools import list_memories, read_business_analysis, read_etl_template, read_memory, write_memory

try:
    from claude_agent_sdk import create_sdk_mcp_server, tool
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    logger.warning("Claude Agent SDK not available. MCP server cannot run.")

if SDK_AVAILABLE:

    @tool("read_etl_template", "Read and return ETL template content", {})
    async def read_etl_template_tool(args: dict[str, Any]) -> dict[str, Any]:
        """MCP tool wrapper for read_etl_template."""
        return read_etl_template()

    @tool("read_business_analysis", "Read business analyst documentation output", {"file_name": str})
    async def read_business_analysis_tool(args: dict[str, Any]) -> dict[str, Any]:
        """MCP tool wrapper for read_business_analysis."""
        return read_business_analysis(args["file_name"])

    @tool("write_memory", "Store user story context in memory organized by layer/datasource/table", {"layer": str, "datasource": str, "table_name": str, "user_story": str, "content": str})
    async def write_memory_tool(args: dict[str, Any]) -> dict[str, Any]:
        """MCP tool wrapper for write_memory."""
        return write_memory(args["layer"], args["datasource"], args["table_name"], args["user_story"], args["content"])

    @tool("read_memory", "Read stored memory for a specific user story", {"layer": str, "datasource": str, "table_name": str, "user_story": str})
    async def read_memory_tool(args: dict[str, Any]) -> dict[str, Any]:
        """MCP tool wrapper for read_memory."""
        return read_memory(args["layer"], args["datasource"], args["table_name"], args["user_story"])

    @tool("list_memories", "List all memories with optional filtering by layer/datasource/table", {"layer": str, "datasource": str, "table_name": str})
    async def list_memories_tool(args: dict[str, Any]) -> dict[str, Any]:
        """MCP tool wrapper for list_memories."""
        return list_memories(args.get("layer"), args.get("datasource"), args.get("table_name"))

    memory_server = create_sdk_mcp_server(name="ba_pyspark_memory", version="2.0.0", tools=[read_etl_template_tool, read_business_analysis_tool, write_memory_tool, read_memory_tool, list_memories_tool])


def main() -> None:
    """Main entry point for MCP server."""
    if not SDK_AVAILABLE:
        logger.error("Claude Agent SDK not installed. Cannot start MCP server.")
        logger.info("Install with: pip install claude-agent-sdk")
        sys.exit(1)
    logger.info("Business Analyst & PySpark Engineer Memory MCP Server configured")
    logger.info("Available tools: read_etl_template, read_business_analysis, write_memory, read_memory, list_memories")
    logger.info("Note: Schema queries now use mcp-server-motherduck directly via mcp__mcp-server-motherduck__query")


if __name__ == "__main__":
    main()
