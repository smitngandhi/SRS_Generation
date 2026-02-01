from google.genai import types
from google.adk.runners import Runner
from google.adk.agents import SequentialAgent , ParallelAgent
import json , shutil , re , subprocess
from pathlib import Path





generate_content_config = types.GenerateContentConfig(
        # 🔒 Enforce machine-readable output
        response_mime_type="application/json",

        # 🎯 Deterministic output (best for schemas)
        temperature=0.0,


        # 🚫 Reduce refusals / partial responses
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



async def create_session(session_service_stateful , app_name: str, user_id: str, session_id: int , intitial_state: dict):
    """Create a session for the user"""
    await session_service_stateful.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=intitial_state
    )


async def create_runner(agent, app_name, session_service_stateful):
    """Create a runner for the agent"""
    return Runner(
        app_name=app_name,
        agent=agent,
        session_service=session_service_stateful
    )


async def create_prompt():
    """Create a prompt for the agent"""
    return types.Content(
        role="user",
        parts=[types.Part(
            text="Based on the provided SRS data, generate the SRS document as per the schema."
        )]
    )


async def generated_response(runner, user_id, session_id, prompt):
    response = None
    async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=prompt,
            ):
                if event.is_final_response():
                    # print("Final response received: ", event.content.parts[0].text)
                    response = event.content.parts[0].text

    return response


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
            print(f"Failed to parse JSON string: {e}")
            return None


async def get_session(session_service_stateful ,app_name , user_id , session_id):
    """Get the session for the user"""
    return await session_service_stateful.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    



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

    return "\n".join(cleaned_lines)




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
    # Check if mmdc is available
    if not shutil.which("mmdc"):
        raise FileNotFoundError(
            "mmdc command not found. Please install it using: npm install -g @mermaid-js/mermaid-cli"
        )
    
    output_png.parent.mkdir(parents=True, exist_ok=True)
    mmd_path = output_png.with_suffix(".mmd")

    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(mermaid_code)

    css_path = Path("srs_engine/static/custom-diagram.css")

    cmd = [
        "C:\\Users\\Smit\\AppData\\Roaming\\npm\\mmdc.CMD",
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
    except subprocess.CalledProcessError as e:
        print(f"❌ mmdc error: {e.stderr}")
        raise