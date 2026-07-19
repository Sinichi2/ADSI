"""Gemini call wrapper: retry + exponential backoff, lazy import, graceful degrade.

Provider is Google Gemini via LangChain (fixed stack). Kept lazy so paths that
don't need an LLM (excel, figma, manual) run with zero LLM deps installed.
"""
import logging
import os
import time

log = logging.getLogger(__name__)


class LLMUnavailable(RuntimeError):
    """Raised when no API key / LLM lib is present. Callers should degrade, not crash."""


def available():
    return bool(os.getenv("GOOGLE_API_KEY"))


def _client(model, api_key):
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise LLMUnavailable("GOOGLE_API_KEY not set — LLM steps skipped.")
    # ponytail: verify the real model string in Google AI Studio; default is a placeholder.
    model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as e:
        raise LLMUnavailable("pip install langchain-google-genai") from e
    return ChatGoogleGenerativeAI(model=model, google_api_key=key, temperature=0)


def call(prompt, model=None, api_key=None, retries=4):
    """Return the model's text response. Retries transient errors with backoff."""
    client = _client(model, api_key)
    delay = 1.0
    for attempt in range(retries):
        try:
            return client.invoke(prompt).content
        except Exception as e:  # noqa: BLE001 - backoff on anything transient
            if attempt == retries - 1:
                log.error("LLM call failed after %d attempts: %s", retries, e)
                raise
            time.sleep(delay)
            delay *= 2
