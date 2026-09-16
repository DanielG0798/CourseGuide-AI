"""MCP server exposing course-policy tools for the M2 agent.

- Initialize a FastMCP server.
- Register tools with @mcp.tool().
- The agent calls these tools through an MCPServerStdio client.
"""
from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Import shared policy loader from the project root.
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.shared.policy_loader import load_policy

mcp = FastMCP("CoursePolicyServer")


@mcp.tool()
def lookup_course_policy(course_id: str) -> str:
    """Return the instructor policy for a given course as readable text."""
    policy = load_policy(course_id, policy_dir="config")

    lines = [
        f"Course: {policy['course_name']} ({policy['course_id']})",
        f"Description: {policy['description']}",
        f"Allowed help levels: {', '.join(policy.get('allowed_help_levels', []))}",
        f"Forbidden help levels: {', '.join(policy.get('forbidden_help_levels', []))}",
        f"Tone: {policy.get('tone', 'helpful')}",
        "Style rules:",
    ]
    for rule in policy.get("style_rules", []):
        lines.append(f"- {rule}")

    return "\n".join(lines)


@mcp.tool()
def classify_help_request(question: str) -> str:
    """Classify the student's question into a help type.

    This is a simple rule-based classifier exposed as an MCP tool so the
    agent can call it instead of hard-coding the logic.
    """
    lowered = question.lower()
    if any(word in lowered for word in ["concept", "what is", "define", "explain"]):
        return "concept"
    if any(word in lowered for word in ["hint", "stuck", "next step", "what should i do"]):
        return "hint"
    if any(word in lowered for word in ["check", "is this right", "verify", "did i"]):
        return "setup_check"
    if any(word in lowered for word in ["similar", "example", "analogy", "practice"]):
        return "analogy"
    return "hint"


@mcp.tool()
def list_available_courses() -> str:
    """Return the list of course policy files found in config/."""
    config_dir = Path("config")
    if not config_dir.exists():
        return "No config directory found."

    courses = [f.stem for f in config_dir.glob("*.yaml") if f.stem != ".gitkeep"]
    return "\n".join(courses) if courses else "No course policies found."


if __name__ == "__main__":
    mcp.run()
