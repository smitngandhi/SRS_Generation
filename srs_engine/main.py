from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.adk.sessions import InMemorySessionService
from srs_engine.agents.introduction_agent import introduction_agent
from srs_engine.schemas.srs_input_schema import SRSRequest
import uuid
from srs_engine.utils.globals import create_session , create_runner , create_prompt , generated_response


app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="srs_engine/static"),
    name="static"
)


templates = Jinja2Templates(directory="srs_engine/templates")

session_service_stateful = InMemorySessionService()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    )


@app.post("/generate_introduction")
async def generate_introduction(srs_data: SRSRequest):
    print("Received SRS Data: ", srs_data)
    session_id = str(uuid.uuid4())

    inputs = srs_data.dict()
    app_name = inputs["project_identity"]["project_name"]
    user_id = "test_user"  # In real scenarios, fetch from auth system

    initial_state = { "user_inputs": inputs }


    await create_session(session_service_stateful, app_name, user_id, session_id , initial_state)

    print("Session created with ID: ", session_id)

    runner = await create_runner(introduction_agent, app_name, session_service_stateful)

    print("Runner created for agent ")
    prompt = await create_prompt()

    print("Prompt created for agent ")

    response = await generated_response(runner , user_id , session_id , prompt)


    print("Generated Introduction Section: ", response)

    return {"introduction_section": response}











