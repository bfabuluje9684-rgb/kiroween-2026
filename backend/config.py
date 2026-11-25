"""
config.py — reads environment variables from a .env file and exposes
them as module-level constants.

BANK_ONLY_MODE is True when AI_API_KEY is absent; in that case the
backend skips all AI calls and draws every question from the built-in
question bank.  A warning is printed to stderr so the developer
knows at a glance why AI generation is disabled.
"""

import os
import sys

from dotenv import load_dotenv

# Load variables from a .env file if one exists alongside this module.
# If the file is absent, python-dotenv silently ignores the call, which
# is intentional — missing .env is treated the same as missing key.
load_dotenv()

AI_API_KEY: str | None = os.getenv("AI_API_KEY") or None
AI_API_URL: str = os.getenv("AI_API_URL", "https://api.anthropic.com/v1/messages")
AI_MODEL: str = os.getenv("AI_MODEL", "claude-haiku-5-5")

# BANK_ONLY_MODE is a convenience flag checked by rate_limiter and
# question_generator so they never attempt an AI call without a key.
BANK_ONLY_MODE: bool = AI_API_KEY is None

if BANK_ONLY_MODE:
    # Print to stderr so the message appears in server logs without
    # contaminating any JSON responses that go to stdout.
    print(
        "WARNING: AI_API_KEY is not set. "
        "The backend will start in bank-only mode and use the built-in "
        "question bank for every session.",
        file=sys.stderr,
    )
