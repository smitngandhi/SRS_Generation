from google.genai import types
import json , shutil , re , subprocess, os
from pathlib import Path





generate_content_config = types.GenerateContentConfig(
    response_mime_type="application/json",
    temperature=0.0,
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.OFF,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.OFF,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.OFF,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.OFF,
        ),
    ],
)


def clean_and_parse_json(raw_response):
    if isinstance(raw_response, dict):
        return raw_response
    
    if not isinstance(raw_response, str):
        return None

    cleaned = raw_response.strip()
    
    # 1. Remove Markdown Code Blocks
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            cleaned = re.sub(r"[\x00-\x1F\x7F]", " ", cleaned) 
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Try to recover JSON that is embedded within other text
            decoder = json.JSONDecoder()
            candidates = []
            for ch in ("{", "["):
                idx = cleaned.find(ch)
                while idx != -1 and len(candidates) < 50:
                    candidates.append(idx)
                    idx = cleaned.find(ch, idx + 1)
            candidates.sort()

            for idx in candidates:
                try:
                    obj, _end = decoder.raw_decode(cleaned[idx:])
                    return obj
                except Exception:
                    continue

            print(f"Failed to parse JSON string: {e}")
            return None


def sanitize_mermaid_output(text: str) -> str | None:
    if not text or not isinstance(text, str):
        return None

    lowered = text.lower()

    refusal_markers = [
        "i can't help",
        "i cannot help",
        "sorry",
        "unable to",
        "as an ai",
        "cannot generate"
    ]
    if any(marker in lowered for marker in refusal_markers):
        return None

    # Remove markdown fences
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*", "", text)
    text = re.sub(r"```$", "", text)

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Normalize labeled arrows
        line = re.sub(
            r"(.*?)-->\s*\|\s*(.*?)\s*\|\s*(.*)",
            r"\1-->| \2 | \3",
            line
        )

        # Normalize arrow variants
        line = re.sub(r"-{3,}>", "-->", line)
        line = re.sub(r"<-{3,}", "<--", line)
        line = re.sub(r"==>", "-->", line)

        cleaned_lines.append(line)

    if not cleaned_lines:
        return None

    first = cleaned_lines[0]
    valid_headers = (
        "flowchart", "graph", "erDiagram",
        "sequenceDiagram", "stateDiagram", "classDiagram"
    )

    if not first.startswith(valid_headers):
        cleaned_lines.insert(0, "flowchart LR")

    merged = "\n".join(cleaned_lines)

    # Heuristic validation: reject likely-truncated diagrams (unbalanced brackets/parens/braces)
    pairs = [
        ("[", "]"),
        ("(", ")"),
        ("{", "}"),
    ]
    for open_ch, close_ch in pairs:
        if merged.count(open_ch) != merged.count(close_ch):
            return None

    return merged




def clean_interface_diagrams(external_interfaces: dict) -> dict:
    """
    Iterates through the external_interfaces dictionary, cleans the mermaid code 
    for each interface type, and returns the updated dictionary.
    """
    # Define the keys to check within the dictionary
    interface_keys = [
        "user_interfaces",
        "hardware_interfaces",
        "software_interfaces",
        "communication_interfaces"
    ]

    for key in interface_keys:
        # Check if the key and the nested path exist to avoid KeyErrors
        try:
            raw_code = external_interfaces[key]["interface_diagram"]["code"]
            
            # Use your existing sanitize function
            cleaned_code = sanitize_mermaid_output(raw_code)
            
            if cleaned_code:
                # Store the cleaned code back into the dictionary
                external_interfaces[key]["interface_diagram"]["code"] = cleaned_code
            else:
                # Optional: Provide a minimal valid fallback if sanitization returns None
                external_interfaces[key]["interface_diagram"]["code"] = "flowchart LR\n    N/A[No Interface Defined]"
        
        except (KeyError, TypeError):
            # Skip if the specific interface section is missing from the input
            continue

    return external_interfaces


def render_mermaid_png(mermaid_code: str, output_png: Path):
    """
    Renders Mermaid code into a PNG file using mmdc (npm).
    """
    mmdc_exe = shutil.which("mmdc") or os.getenv("MMDC_PATH")
    if not mmdc_exe:
        print(
            "❌ mmdc command not found. Install it with: npm install -g @mermaid-js/mermaid-cli "
            "and ensure it is on PATH (or set MMDC_PATH). Skipping diagram rendering."
        )
        return False
    
    output_png.parent.mkdir(parents=True, exist_ok=True)
    mmd_path = output_png.with_suffix(".mmd")

    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(mermaid_code)

    css_path = Path("srs_engine/static/custom-diagram.css")

    cmd = [
        mmdc_exe,
        "-i", str(mmd_path),
        "-o", str(output_png),
        "-w", "2400",
        "-H", "1600",
        "-t", "forest",
        "-b", "white",
        "-s", "2"
    ]


    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Mermaid diagram saved: {output_png}")
        return True
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        stdout = (e.stdout or "").strip()
        print(f"❌ mmdc error (exit {e.returncode}) while rendering {output_png}: {stderr or stdout or 'unknown error'}")
        return False
