#!/usr/bin/env python3
"""On-demand MCP client for connecting to MCP servers without loading them into Claude context."""
import os
import json
import subprocess
from pathlib import Path
from typing import Any


class OnDemandMCPClient:
    """Client for connecting to MCP servers on-demand without polluting Claude context."""

    def __init__(self, registry_path: str = None):
        if registry_path is None:
            skill_dir = Path(__file__).parent.parent
            registry_path = skill_dir / "mcp_configs" / "registry.json"
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
        self.active_servers = {}

    def _load_registry(self) -> dict[str, Any]:
        """Load MCP server registry."""
        if not self.registry_path.exists():
            return {"servers": {}}
        with open(self.registry_path) as f:
            return json.load(f)

    def list_available_servers(self) -> list[str]:
        """List all registered MCP servers."""
        return list(self.registry.get("servers", {}).keys())

    def get_server_info(self, server_name: str) -> dict[str, Any]:
        """Get information about a registered MCP server."""
        return self.registry.get("servers", {}).get(server_name, {})

    def start_server(self, server_name: str) -> subprocess.Popen:
        """
        Start an MCP server process.

        NOTE: This is a basic implementation. For production use, you'd want:
        - Proper MCP protocol implementation (stdio transport)
        - Error handling and retries
        - Server health checks
        - Process cleanup
        """
        server_config = self.get_server_info(server_name)
        if not server_config:
            raise ValueError(f"Server '{server_name}' not found in registry")
        env = os.environ.copy()
        for key, value in server_config.get("env", {}).items():
            if value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env[key] = os.getenv(env_var, "")
            else:
                env[key] = value
        command = [server_config["command"]] + server_config.get("args", [])
        process = subprocess.Popen(command, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.active_servers[server_name] = process
        return process

    def stop_server(self, server_name: str):
        """Stop an active MCP server process."""
        if server_name in self.active_servers:
            self.active_servers[server_name].terminate()
            self.active_servers[server_name].wait(timeout=5)
            del self.active_servers[server_name]

    def cleanup(self):
        """Stop all active MCP servers."""
        for server_name in list(self.active_servers.keys()):
            self.stop_server(server_name)


def main():
    """CLI for testing MCP client."""
    import sys
    client = OnDemandMCPClient()
    if len(sys.argv) < 2:
        print("Available commands:")
        print("  list - List all registered MCP servers")
        print("  info <server> - Get server information")
        print("  start <server> - Start an MCP server")
        sys.exit(1)
    command = sys.argv[1]
    if command == "list":
        servers = client.list_available_servers()
        print("Registered MCP servers:")
        for server in servers:
            info = client.get_server_info(server)
            print(f"  - {server}: {info.get('description', 'No description')}")
    elif command == "info" and len(sys.argv) > 2:
        server_name = sys.argv[2]
        info = client.get_server_info(server_name)
        print(json.dumps(info, indent=2))
    elif command == "start" and len(sys.argv) > 2:
        server_name = sys.argv[2]
        print(f"Starting MCP server: {server_name}")
        client.start_server(server_name)
        print("Note: This is a basic implementation. Full MCP protocol support needed for production.")


if __name__ == "__main__":
    main()
