import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LlmSelection:
    provider: str  # "groq" | "gemini"
    model: str


def _normalize_groq_model(model: str) -> str:
    m = (model or "").strip()
    if not m:
        return "auto"
    if m.lower() in ("auto", "default"):
        return "auto"
    if m.startswith("groq/"):
        m = m[len("groq/") :]
    # Accept LiteLLM-style vendor prefixes like "meta-llama/llama-3.1-8b-instant"
    if "/" in m:
        m = m.split("/")[-1]
    return m


def _normalize_gemini_model(model: str) -> str:
    m = (model or "").strip()
    if not m:
        return "gemini-1.5-flash"
    if m.startswith("gemini/"):
        m = m[len("gemini/") :]
    return m


def get_llm_selection() -> LlmSelection:
    """
    Returns the configured LLM provider + model for *direct* API usage.

    Supported env vars:
      - LLM_PROVIDER: "groq" or "gemini"
      - LLM_MODEL: optional override (provider-specific model name; LiteLLM-style prefixes are tolerated)
      - GROQ_MODEL, GEMINI_MODEL
    """
    provider = (os.getenv("LLM_PROVIDER") or "groq").strip().lower()
    if provider not in ("groq", "gemini"):
        provider = "groq"

    override_model = (os.getenv("LLM_MODEL") or "").strip()
    if override_model:
        if provider == "gemini":
            return LlmSelection(provider="gemini", model=_normalize_gemini_model(override_model))
        return LlmSelection(provider="groq", model=_normalize_groq_model(override_model))

    if provider == "gemini":
        model = _normalize_gemini_model(os.getenv("GEMINI_MODEL") or "gemini-1.5-flash")
        return LlmSelection(provider="gemini", model=model)

    model = _normalize_groq_model(os.getenv("GROQ_MODEL") or "auto")
    return LlmSelection(provider="groq", model=model)


def ensure_api_key_configured(selection: LlmSelection) -> None:
    if selection.provider == "groq":
        if not (os.getenv("GROQ_API_KEY") or "").strip():
            raise RuntimeError("Missing GROQ_API_KEY for Groq provider.")
        return
    if selection.provider == "gemini":
        if not ((os.getenv("GEMINI_API_KEY") or "").strip() or (os.getenv("GOOGLE_API_KEY") or "").strip()):
            raise RuntimeError("Missing GEMINI_API_KEY (or GOOGLE_API_KEY) for Gemini provider.")
        return
    raise RuntimeError(f"Unsupported LLM_PROVIDER: {selection.provider}")
