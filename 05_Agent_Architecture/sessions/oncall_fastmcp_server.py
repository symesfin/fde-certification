"""The on-call capability as a FastMCP server, in a process of its own.

Run from the repository root (it speaks MCP over stdio):
    uv run --group week5 python 05_Agent_Architecture/sessions/oncall_fastmcp_server.py
Or point an MCP client at that command -- including Claude Code, via .mcp.json.
`show_banner=False` also skips FastMCP's PyPI update check, which runs with the banner.
"""

from fastmcp import FastMCP

ONCALL = {
    "atlas": {"team": "Tracking Platform", "channel": "#team-tracking", "pager": "tracking-oncall"},
    "ledger": {"team": "Revenue Systems", "channel": "#team-revenue", "pager": "revenue-oncall"},
    "warehouse gateway": {"team": "Depot Systems", "channel": "#team-depot", "pager": "depot-oncall"},
    "postgres": {"team": "Data Platform", "channel": "#team-data", "pager": "data-oncall-24x7"},
}

server = FastMCP("oncall")


@server.tool
def who_is_oncall(service: str) -> dict:
    """Find which team owns a service and how to reach them."""
    key = service.strip().lower()
    for name, info in ONCALL.items():
        if key in name or name in key:
            return {"service": name, **info}
    return {"error": f"unknown service: {service}", "known": sorted(ONCALL)}


if __name__ == "__main__":
    server.run(show_banner=False)  # stdio by default
