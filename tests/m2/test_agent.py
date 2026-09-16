"""Tests for the Milestone 2 agent prototype.

These tests run the agent against the cases defined in `test_cases.yaml`.
Because the agent calls a live model, the checks look for expected keywords
rather than exact string matches.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.m2.agent import ask


CASES_PATH = Path(__file__).with_name("test_cases.yaml")


def load_test_cases() -> list[dict]:
    with open(CASES_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("test_cases", [])


@pytest.mark.asyncio
@pytest.mark.parametrize("case", load_test_cases(), ids=lambda c: c["id"])
async def test_agent_response_contains_keywords(case: dict):
    response = await ask(case["course_id"], case["question"])
    response_lower = response.lower()

    missing = [
        kw for kw in case["expected_keywords"]
        if kw.lower() not in response_lower
    ]
    assert not missing, f"Missing keywords {missing} in response:\n{response}"
