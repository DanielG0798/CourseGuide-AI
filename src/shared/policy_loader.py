"""Load and validate instructor course policies."""
from __future__ import annotations

from pathlib import Path

import yaml


DEFAULT_POLICY = {
    "course_id": "default",
    "course_name": "Default Course",
    "description": "Fallback policy when no specific course policy is found.",
    "allowed_help_levels": ["concept", "hint", "next_step"],
    "forbidden_help_levels": ["full_solution", "direct_answer"],
    "tone": "encouraging and concise",
    "approved_sources": [],
    "style_rules": [
        "Ask a follow-up question before giving a hint.",
        "Never provide the final numerical answer.",
    ],
}


def load_policy(course_id: str, policy_dir: Path | str = "config") -> dict:
    """Load a course policy YAML file or return the default policy.

    Args:
        course_id: The identifier for the course, e.g. "physics_101".
        policy_dir: Folder containing policy YAML files.

    Returns:
        A dictionary with the policy for that course.
    """
    directory = Path(policy_dir)
    candidate = directory / f"{course_id}.yaml"

    if candidate.exists():
        with open(candidate, "r", encoding="utf-8") as f:
            policy = yaml.safe_load(f) or {}
        # Merge with defaults so required keys always exist.
        return {**DEFAULT_POLICY, **policy}

    # If no exact match, return the default policy so the agent can still run.
    return {**DEFAULT_POLICY, "course_id": course_id}
