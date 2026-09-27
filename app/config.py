"""Application Configuration Module.

Loads configuration parameters and API keys from environment variables and
.env files located in the repository or workspace root.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
ANALYTICS_DIR = DATA_DIR / "analytics"

# Ensure required storage directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from repo .env or workspace .env (Rule 6)
if (BASE_DIR / ".env").exists():
    load_dotenv(dotenv_path=BASE_DIR / ".env")
elif (WORKSPACE_DIR / ".env").exists():
    load_dotenv(dotenv_path=WORKSPACE_DIR / ".env")
else:
    load_dotenv()


class Settings:
    """Application runtime settings and configuration container."""

    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_API_BASE: str = os.getenv(
        "OPENROUTER_API_BASE", "https://openrouter.ai/api/v1"
    )
    CREWAI_MODEL: str = os.getenv(
        "CREWAI_MODEL", "openrouter/google/gemini-2.5-flash"
    )
    CREWAI_MAX_TOKENS: int = int(os.getenv("CREWAI_MAX_TOKENS", "2048"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DATA_PATH: Path = DATA_DIR / "workouts.json"
    ANALYTICS_DIR: Path = ANALYTICS_DIR


settings = Settings()
