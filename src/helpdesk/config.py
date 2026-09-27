"""Central configuration: the model and retry behaviour live in one place."""

import os

from dotenv import load_dotenv
from google.adk.models import Gemini
from google.genai import types

load_dotenv()

MODEL_ID = os.getenv("HELPDESK_MODEL", "gemini-3.8-flash")

RETRY = types.HttpRetryOptions(
    attempts=5,
    initial_delay=2.0,
    max_delay=30.0,
    http_status_codes=[429, 500, 503],
)


def model() -> Gemini:
    """Return the Gemini model every agent in this repo uses."""
    return Gemini(model=MODEL_ID, retry_options=RETRY)
