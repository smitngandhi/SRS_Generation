from google.genai import types
from google.adk.runners import Runner
from google.adk.agents import SequentialAgent , ParallelAgent
import json
import re




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
                    print("Final response received: ", event.content.parts[0].text)
                    
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
    
    # 2. FIX: Handle unescaped control characters (Newlines/Tabs) 
    # This replaces literal newlines inside the string with escaped '\n'
    # but only if they are not the start of a new JSON key/structure.
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            # More aggressive cleaning: remove actual control characters
            # except those that are part of JSON structure
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
    

