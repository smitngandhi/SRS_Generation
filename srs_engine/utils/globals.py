from google.genai import types
from google.adk.runners import Runner

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
            text="Based on the provided SRS data, generate the Introduction section of the SRS document as per the schema."
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

