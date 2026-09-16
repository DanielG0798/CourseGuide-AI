"""Shared configuration and environment loading."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"


def load_yaml(path: str | Path) -> dict:
    """Load a YAML file from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_required_env(key: str) -> str:
    """Return an environment variable or raise a clear error."""
    value = os.getenv(key)
    if not value:
        raise ValueError(
            f"Missing required environment variable: {key}. "
            f"Set it in a .env file or export it before running."
        )
    return value


def model_client_config() -> dict:
    """Return the active model client configuration."""
    return {
        "provider": os.getenv("MODEL_PROVIDER", "byom"),
        "api_key": os.getenv("BYOM_API_KEY", os.getenv("OPENAI_API_KEY", "")),
        "base_url": os.getenv("MODEL_BASE_URL", "https://api.openai.com/v1"),
        "model": os.getenv("MODEL_NAME", "gpt-4o-mini"),
        "fallback_model": os.getenv("FALLBACK_MODEL", "nrp-open-llm"),
        "fallback_base_url": os.getenv("FALLBACK_BASE_URL", ""),
    }
