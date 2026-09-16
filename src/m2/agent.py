"""Milestone 2 single-tool agent prototype.

- Configure an OpenAI-compatible client pointing at BYOM or NRP.
- Use the OpenAI Agents SDK (`Agent`, `Runner`).
- Attach an MCP server (stdio) so the agent can look up course policies
  and classify help requests through tools.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

from agents import Agent, Runner, set_default_openai_api, set_default_openai_client
from agents.mcp import MCPServerStdio, MCPServerStdioParams
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Allow importing shared modules when running as a script.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.shared.config import get_required_env
from src.shared.tracing import ConsoleTracingProcessor
from agents.tracing import set_trace_processors

load_dotenv()

# Configure tracing so we can see token usage in the console.
set_trace_processors([ConsoleTracingProcessor()])

MCP_SCRIPT = ROOT / "mcp_servers" / "course_policy_mcp.py"

INSTRUCTIONS = """
You are CourseGuide AI, a course-specific learning assistant.

Your job is to help the student reason through their work without doing the
assignment for them.

Before you answer a student question, follow these steps:
1. Call `classify_help_request` to decide what kind of help the student wants.
2. Call `lookup_course_policy` for the given course_id to see what the
   instructor allows.
3. Respond according to the policy: be encouraging, ask what the student has
   already tried, and give the smallest useful next step. Never provide a full
   solution or final numerical answer unless the policy explicitly allows it.

If the student asks which courses are available, use `list_available_courses`.
"""


def configure_client() -> AsyncOpenAI:
    """Create an AsyncOpenAI client from environment variables.

    Defaults point at BYOM, but setting NRP_BASE_URL and NRP_API_KEY
    switches the agent to the NRP fallback.
    """
    base_url = os.getenv("MODEL_BASE_URL") or os.getenv("NRP_BASE_URL")
    api_key = os.getenv("BYOM_API_KEY") or os.getenv("NRP_API_KEY")
    if not base_url:
        raise ValueError("Set MODEL_BASE_URL or NRP_BASE_URL in your environment.")
    if not api_key:
        raise ValueError("Set BYOM_API_KEY or NRP_API_KEY in your environment.")
    return AsyncOpenAI(base_url=base_url, api_key=api_key)


async def ask(course_id: str, question: str, model: str | None = None) -> str:
    """Run the M2 agent on a single student question.

    Returns the agent's final response as a string.
    """
    client = configure_client()
    set_default_openai_client(client, use_for_tracing=False)
    set_default_openai_api("chat_completions")

    async with MCPServerStdio(
        name="CoursePolicyServer",
        params=MCPServerStdioParams(
            command="python",
            args=[str(MCP_SCRIPT)],
        ),
        client_session_timeout_seconds=90,
    ) as mcp_server:
        agent = Agent(
            name="CourseGuideM2",
            instructions=INSTRUCTIONS,
            mcp_servers=[mcp_server],
            model=model or os.getenv("MODEL_NAME", "gpt-oss"),
        )

        user_input = f"Course ID: {course_id}\nStudent question: {question}"
        result = await Runner.run(agent, user_input)
        return result.final_output


def main():
    parser = argparse.ArgumentParser(description="Run the CourseGuide AI M2 prototype")
    parser.add_argument("--course", default="physics_101", help="Course identifier")
    parser.add_argument("--question", required=True, help="Student question")
    parser.add_argument("--model", default=None, help="Model name override")
    args = parser.parse_args()

    response = asyncio.run(ask(args.course, args.question, args.model))
    print("\n--- Agent response ---\n")
    print(response)


if __name__ == "__main__":
    main()
