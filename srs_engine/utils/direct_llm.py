import os
import json
from typing import Optional
import time

import requests
from google import genai
from google.genai import types

from .llm_config import LlmSelection


class LlmAuthError(RuntimeError):
    pass


class LlmProviderError(RuntimeError):
    pass


GROQ_FALLBACK_MODELS = (
    "llama-4-scout-17b-16e-instruct",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
)


def _parse_json_object_best_effort(text: str) -> dict | None:
    if not text or not isinstance(text, str):
        return None

    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        obj = json.loads(cleaned)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass

    decoder = json.JSONDecoder()
    idx = cleaned.find("{")
    tries = 0
    while idx != -1 and tries < 50:
        tries += 1
        try:
            obj, _end = decoder.raw_decode(cleaned[idx:])
            return obj if isinstance(obj, dict) else None
        except Exception:
            idx = cleaned.find("{", idx + 1)
            continue
    return None


def _groq_post(*, api_key: str, payload: dict, timeout_s: int) -> requests.Response:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    return requests.post(url, headers=headers, json=payload, timeout=timeout_s)


def _groq_post_with_retry(*, api_key: str, payload: dict, timeout_s: int, retries: int = 2) -> requests.Response:
    attempt = 0
    last_exc: Exception | None = None

    while attempt <= retries:
        try:
            resp = _groq_post(api_key=api_key, payload=payload, timeout_s=timeout_s)
        except requests.RequestException as e:
            last_exc = e
            resp = None

        if resp is None:
            if attempt == retries:
                raise LlmProviderError(f"Groq request failed: {last_exc}") from last_exc
            time.sleep(0.4 * (attempt + 1))
            attempt += 1
            continue

        # Retry on transient errors / rate limiting
        if resp.status_code in (429, 500, 502, 503, 504):
            if attempt == retries:
                return resp
            time.sleep(0.5 * (attempt + 1))
            attempt += 1
            continue

        return resp

    raise LlmProviderError("Groq request failed after retries.")

def _is_groq_model_not_found(resp: requests.Response) -> bool:
    if resp.status_code != 404:
        return False
    try:
        data = resp.json()
    except Exception:
        return False
    err = data.get("error") or {}
    code = (err.get("code") or "").strip()
    msg = (err.get("message") or "").lower()
    return code == "model_not_found" or "does not exist" in msg


def _groq_list_models(*, api_key: str, timeout_s: int) -> list[str]:
    url = "https://api.groq.com/openai/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout_s)
    except requests.RequestException as e:
        raise LlmProviderError(f"Groq model listing failed: {e}") from e

    if resp.status_code == 401:
        raise LlmAuthError("Invalid GROQ_API_KEY.")
    if resp.status_code >= 400:
        raise LlmProviderError(f"Groq model listing error {resp.status_code}: {resp.text}")

    try:
        data = resp.json()
        items = data.get("data") or []
        ids = []
        for item in items:
            mid = (item.get("id") or "").strip()
            if mid:
                ids.append(mid)
        return ids
    except Exception as e:
        raise LlmProviderError(f"Failed to parse Groq model list: {e}") from e


def _pick_groq_model(available: list[str]) -> str:
    if not available:
        raise LlmProviderError("Groq returned no available models.")

    preferred = list(GROQ_FALLBACK_MODELS) + [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ]

    available_set = set(available)
    for candidate in preferred:
        if candidate in available_set:
            return candidate

    for mid in available:
        if "llama" in mid.lower():
            return mid

    return available[0]


def _groq_chat_completion(
    *,
    model: str,
    system: str,
    user: str,
    temperature: float = 0.0,
    max_output_tokens: int = 4096,
    timeout_s: int = 60,
    expect_json: bool = False,
) -> str:
    api_key = (os.getenv("GROQ_API_KEY") or "").strip()
    if not api_key:
        raise LlmAuthError("Missing GROQ_API_KEY.")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_output_tokens,
    }

    if (model or "").strip().lower() in ("auto", ""):
        available = _groq_list_models(api_key=api_key, timeout_s=timeout_s)
        available_set = set(available)
        candidates: list[str] = []
        for candidate in GROQ_FALLBACK_MODELS:
            if candidate in available_set and candidate not in candidates:
                candidates.append(candidate)
        for mid in available:
            if mid not in candidates:
                candidates.append(mid)

        first_success_text: str | None = None
        errors: list[str] = []

        for candidate in candidates:
            payload["model"] = candidate
            try:
                resp = _groq_post_with_retry(api_key=api_key, payload=payload, timeout_s=timeout_s)
            except Exception as e:
                errors.append(f"{candidate}: request_error {str(e)[:300]}")
                continue

            if resp.status_code == 401:
                raise LlmAuthError("Invalid GROQ_API_KEY.")
            if resp.status_code < 400:
                try:
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"]
                    if first_success_text is None:
                        first_success_text = text
                    if not expect_json:
                        return text
                    if _parse_json_object_best_effort(text) is not None:
                        return text
                    continue
                except Exception as e:
                    raise LlmProviderError(f"Failed to parse Groq response: {e}") from e
            else:
                try:
                    errors.append(f"{candidate}: {resp.status_code} {resp.text[:300]}")
                except Exception:
                    errors.append(f"{candidate}: {resp.status_code}")
            # Otherwise, try the next available model
            continue

        if first_success_text is not None:
            return first_success_text

        raise LlmProviderError(
            "No available Groq models succeeded for chat completions. "
            "Set GROQ_MODEL=auto or a known working model id for your key. "
            + (f"Last errors: {errors[-1]}" if errors else "")
        )

    try:
        resp = _groq_post_with_retry(api_key=api_key, payload=payload, timeout_s=timeout_s)
    except Exception as e:
        raise LlmProviderError(str(e)) from e

    if resp.status_code == 401:
        raise LlmAuthError("Invalid GROQ_API_KEY.")

    if _is_groq_model_not_found(resp):
        available = _groq_list_models(api_key=api_key, timeout_s=timeout_s)
        # Try preferred + whatever is available
        for fallback_model in GROQ_FALLBACK_MODELS:
            if fallback_model == model:
                continue
            retry_payload = dict(payload)
            retry_payload["model"] = fallback_model
            try:
                retry_resp = _groq_post_with_retry(api_key=api_key, payload=retry_payload, timeout_s=timeout_s)
            except Exception:
                continue
            if retry_resp.status_code == 401:
                raise LlmAuthError("Invalid GROQ_API_KEY.")
            if retry_resp.status_code < 400:
                try:
                    data = retry_resp.json()
                    return data["choices"][0]["message"]["content"]
                except Exception as e:
                    raise LlmProviderError(f"Failed to parse Groq response: {e}") from e

        # Finally, try any model Groq reports as available
        for candidate in available:
            if candidate == model:
                continue
            retry_payload = dict(payload)
            retry_payload["model"] = candidate
            try:
                retry_resp = _groq_post_with_retry(api_key=api_key, payload=retry_payload, timeout_s=timeout_s)
            except Exception:
                continue
            if retry_resp.status_code == 401:
                raise LlmAuthError("Invalid GROQ_API_KEY.")
            if retry_resp.status_code < 400:
                try:
                    data = retry_resp.json()
                    return data["choices"][0]["message"]["content"]
                except Exception as e:
                    raise LlmProviderError(f"Failed to parse Groq response: {e}") from e

        raise LlmProviderError(
            "Configured Groq model is not available for this API key. "
            f"Set GROQ_MODEL=auto or one of the available models: {', '.join(available[:20])}"
        )

    if resp.status_code >= 400:
        raise LlmProviderError(f"Groq error {resp.status_code}: {resp.text}")

    try:
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise LlmProviderError(f"Failed to parse Groq response: {e}") from e


def _gemini_generate(
    *,
    model: str,
    system: str,
    user: str,
    temperature: float = 0.0,
    max_output_tokens: int = 4096,
    response_mime_type: Optional[str] = None,
) -> str:
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip() or (os.getenv("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        raise LlmAuthError("Missing GEMINI_API_KEY (or GOOGLE_API_KEY).")

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        response_mime_type=response_mime_type,
    )
    try:
        resp = client.models.generate_content(model=model, contents=user, config=config)
        text = (resp.text or "").strip()
        if not text:
            raise LlmProviderError("Gemini returned empty response.")
        return text
    except Exception as e:
        msg = str(e).lower()
        if "api key" in msg and ("invalid" in msg or "not valid" in msg):
            raise LlmAuthError("Invalid GEMINI_API_KEY / GOOGLE_API_KEY.") from e
        raise LlmProviderError(f"Gemini request failed: {e}") from e


def generate(
    *,
    selection: LlmSelection,
    system: str,
    user: str,
    temperature: float = 0.0,
    max_output_tokens: int = 4096,
    expect_json: bool = False,
) -> str:
    if selection.provider == "groq":
        try:
            return _groq_chat_completion(
                model=selection.model,
                system=system,
                user=user,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                expect_json=expect_json,
            )
        except LlmProviderError:
            # Optional resilience: if Gemini is configured, fallback automatically.
            gemini_key = (os.getenv("GEMINI_API_KEY") or "").strip() or (os.getenv("GOOGLE_API_KEY") or "").strip()
            gemini_model = (os.getenv("GEMINI_MODEL") or "gemini-1.5-flash").strip()
            if gemini_key:
                return _gemini_generate(
                    model=gemini_model.replace("gemini/", ""),
                    system=system,
                    user=user,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    response_mime_type="application/json" if expect_json else None,
                )
            raise
    if selection.provider == "gemini":
        return _gemini_generate(
            model=selection.model,
            system=system,
            user=user,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json" if expect_json else None,
        )
    raise LlmProviderError(f"Unsupported provider: {selection.provider}")
