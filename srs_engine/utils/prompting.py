import json
from typing import Any
import re


def substitute_vars(template: str, **vars: Any) -> str:
    """
    Safe placeholder replacement for prompt templates that contain JSON examples.

    Replaces only exact tokens like "{user_inputs}" without interpreting other braces.
    Dicts/lists are JSON-serialized; other values are stringified.
    """
    out = template
    for key, value in vars.items():
        token = "{" + key + "}"
        if token not in out:
            continue
        if isinstance(value, (dict, list)):
            replacement = json.dumps(value, ensure_ascii=False)
        else:
            replacement = "" if value is None else str(value)
        out = out.replace(token, replacement)
    return out


def compact_prompt(text: str) -> str:
    """
    Reduces prompt size without changing meaning:
    - Removes fenced code blocks (```...```) which are usually examples
    - Collapses excessive blank lines
    """
    if not text or not isinstance(text, str):
        return ""

    # Remove fenced code blocks (including ```json, ```mermaid, etc.)
    compacted = re.sub(r"```[\s\S]*?```", "", text)

    # Collapse 3+ newlines into 2
    compacted = re.sub(r"\n{3,}", "\n\n", compacted)

    return compacted.strip()
