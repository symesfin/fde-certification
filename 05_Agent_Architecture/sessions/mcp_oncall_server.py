"""An MCP server exposing one tool over stdio.

Run standalone:  python mcp_oncall_server.py
Or point an MCP client at it -- including Claude Code, via .mcp.json.
"""
import json
from mcp.server import MCPServer

ONCALL = {
    "atlas": {
        "team": "Tracking Platform",
        "channel": "#team-tracking",
        "pager": "tracking-oncall"
    },
    "ledger": {
        "team": "Revenue Systems",
        "channel": "#team-revenue",
        "pager": "revenue-oncall"
    },
    "warehouse gateway": {
        "team": "Depot Systems",
        "channel": "#team-depot",
        "pager": "depot-oncall"
    },
    "postgres": {
        "team": "Data Platform",
        "channel": "#team-data",
        "pager": "data-oncall-24x7"
    }
}

server = MCPServer("oncall")


@server.tool()
def who_is_oncall(service: str) -> str:
    """Find which team owns a service and how to reach them."""
    key = service.strip().lower()
    for name, info in ONCALL.items():
        if key in name or name in key:
            return json.dumps({"service": name, **info})
    return json.dumps({"error": f"unknown service: {service}"})


if __name__ == "__main__":
    server.run()          # stdio by default
