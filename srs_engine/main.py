from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
from srs_engine.schemas.srs_input_schema import SRSRequest
from srs_engine.schemas.section_enhancement_schema import (
    SectionEnhancementRequest,
    SectionEnhancementResponse,
)
from srs_engine.utils.globals import (
    clean_and_parse_json,
    clean_interface_diagrams,
    render_mermaid_png)
from srs_engine.utils.llm_config import get_llm_selection, ensure_api_key_configured
from srs_engine.utils.direct_llm import generate, LlmAuthError, LlmProviderError
from srs_engine.utils.prompting import substitute_vars, compact_prompt
from dotenv import load_dotenv, find_dotenv
from srs_engine.agents.introduction_agent.prompt import AGENT_DESCRIPTION as INTRO_DESC, AGENT_INSTRUCTION as INTRO_INST
from srs_engine.agents.overall_description_agent.prompt import AGENT_DESCRIPTION as OVERALL_DESC, AGENT_INSTRUCTION as OVERALL_INST
from srs_engine.agents.system_features_agent.prompt import AGENT_DESCRIPTION as FEATURES_DESC, AGENT_INSTRUCTION as FEATURES_INST
from srs_engine.agents.external_interfaces_agent.prompt import AGENT_DESCRIPTION as EXT_DESC, AGENT_INSTRUCTION as EXT_INST
from srs_engine.agents.nfr_agent.prompt import AGENT_DESCRIPTION as NFR_DESC, AGENT_INSTRUCTION as NFR_INST
from srs_engine.agents.glossary_agent.prompt import AGENT_DESCRIPTION as GLOSSARY_DESC, AGENT_INSTRUCTION as GLOSSARY_INST
from srs_engine.agents.assumptions_agent.prompt import AGENT_DESCRIPTION as ASSUMPTIONS_DESC, AGENT_INSTRUCTION as ASSUMPTIONS_INST
from srs_engine.agents.section_enhancer_agent.prompt import AGENT_DESCRIPTION as ENHANCE_DESC, AGENT_INSTRUCTION as ENHANCE_INST
from pathlib import Path
from datetime import datetime
from srs_engine.utils.srs_document_generator import generate_srs_document
from fastapi import HTTPException

today = datetime.today().strftime("%m/%d/%Y")

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="srs_engine/static"),
    name="static"
)


templates = Jinja2Templates(directory="srs_engine/templates")
load_dotenv(find_dotenv(), override=False)
load_dotenv(Path(__file__).with_name(".env"), override=False)
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    )

def _llm_error_to_http(exc: Exception) -> HTTPException:
    if isinstance(exc, LlmAuthError):
        return HTTPException(status_code=401, detail=str(exc))
    if isinstance(exc, LlmProviderError):
        return HTTPException(status_code=502, detail=str(exc))
    if isinstance(exc, RuntimeError) and "missing" in str(exc).lower():
        return HTTPException(status_code=500, detail=str(exc))
    return HTTPException(status_code=502, detail=f"LLM request failed: {exc}")


def _generate_json_section(desc: str, inst: str, *, selection, section_name: str, **vars) -> dict:
    system = substitute_vars(desc, **vars).strip()
    user = substitute_vars(inst, **vars).strip()

    # Groq often has tighter context limits than Gemini; remove large examples from prompts.
    if getattr(selection, "provider", "") == "groq":
        system = compact_prompt(system)
        user = compact_prompt(user)

    raw = generate(
        selection=selection,
        system=system,
        user=user,
        temperature=0.0,
        max_output_tokens=4096,
        expect_json=True,
    )
    parsed = clean_and_parse_json(raw)
    if isinstance(parsed, dict):
        return parsed

    # Retry once with stronger JSON-only constraints + reduced verbosity (avoids truncation).
    retry_system = (
        system
        + "\n\nCRITICAL:\n"
        + "- Return ONLY a valid JSON object.\n"
        + "- No markdown/code fences.\n"
        + "- If the response might be truncated, reduce verbosity while keeping required keys.\n"
    )
    raw2 = generate(
        selection=selection,
        system=retry_system,
        user=user,
        temperature=0.0,
        max_output_tokens=4096,
        expect_json=True,
    )
    parsed2 = clean_and_parse_json(raw2)
    if isinstance(parsed2, dict):
        return parsed2

    # Final attempt: ask the model to repair/format its own output into valid JSON.
    repair_system = (
        "You are a strict JSON repair tool.\n"
        "Return ONLY a valid JSON object (no markdown, no prose).\n"
        "Do not add new keys beyond what is already present; fix formatting issues.\n"
        "If the content is incomplete, return a minimal valid JSON object preserving the same top-level keys.\n"
    )
    repair_user = f"Convert the following into valid JSON only:\n\n{raw2}"
    raw3 = generate(
        selection=selection,
        system=repair_system,
        user=repair_user,
        temperature=0.0,
        max_output_tokens=4096,
        expect_json=True,
    )
    parsed3 = clean_and_parse_json(raw3)
    if isinstance(parsed3, dict):
        return parsed3

    raise LlmProviderError(f"Model did not return valid JSON for section: {section_name}.")


def _generate_text_section(desc: str, inst: str, *, selection, **vars) -> str:
    system = substitute_vars(desc, **vars).strip()
    user = substitute_vars(inst, **vars).strip()
    if getattr(selection, "provider", "") == "groq":
        system = compact_prompt(system)
        user = compact_prompt(user)
    raw = generate(
        selection=selection,
        system=system,
        user=user,
        temperature=0.0,
        max_output_tokens=1024,
        expect_json=False,
    )
    return (raw or "").strip()


@app.post("/enhance_section", response_model=SectionEnhancementResponse)
async def enhance_section(payload: SectionEnhancementRequest):
    """
    Enhances short/unstructured input into SRS-ready content for a given section.
    """
    selection = get_llm_selection()
    try:
        ensure_api_key_configured(selection)
        content = _generate_text_section(
            ENHANCE_DESC,
            ENHANCE_INST,
            selection=selection,
            section_type=payload.section_type,
            user_input=payload.user_input,
        )
        if not content:
            raise LlmProviderError("Enhancement returned empty content.")
        return SectionEnhancementResponse(content=content)
    except Exception as e:
        raise _llm_error_to_http(e)


@app.post("/generate_srs")
async def generate_srs(srs_data: SRSRequest):

    selection = get_llm_selection()
    try:
        ensure_api_key_configured(selection)
    except Exception as e:
        raise _llm_error_to_http(e)

    print("Received SRS Data: ", srs_data)

    inputs = srs_data.dict()
    project_name = inputs["project_identity"]["project_name"] # will be used later
    author_list = inputs["project_identity"]["author"] # will be used later
    organization_name = inputs["project_identity"]["organization"] # will be used later

    print(f'''Project Name: {project_name}''')
    print(f'''Authors: {author_list}''')
    print(f'''Organization: {organization_name}''')
    try:
        introduction_section = _generate_json_section(
            INTRO_DESC, INTRO_INST, selection=selection, section_name="Introduction", user_inputs=inputs
        )
        overall_description_section = _generate_json_section(
            OVERALL_DESC, OVERALL_INST, selection=selection, section_name="Overall Description", user_inputs=inputs
        )
        system_features_section = _generate_json_section(
            FEATURES_DESC, FEATURES_INST, selection=selection, section_name="System Features", user_inputs=inputs
        )
        external_interfaces_section = _generate_json_section(
            EXT_DESC, EXT_INST, selection=selection, section_name="External Interfaces", user_inputs=inputs
        )
        nfr_section = _generate_json_section(
            NFR_DESC, NFR_INST, selection=selection, section_name="Non-Functional Requirements", user_inputs=inputs
        )

        glossary_section = _generate_json_section(
            GLOSSARY_DESC,
            GLOSSARY_INST,
            selection=selection,
            section_name="Glossary",
            user_inputs=inputs,
            introduction_section=introduction_section,
            overall_description_section=overall_description_section,
            system_features_section=system_features_section,
            nfr_section=nfr_section,
        )

        assumptions_section = _generate_json_section(
            ASSUMPTIONS_DESC,
            ASSUMPTIONS_INST,
            selection=selection,
            section_name="Assumptions",
            user_inputs=inputs,
            introduction_section=introduction_section,
            overall_description_section=overall_description_section,
            system_features_section=system_features_section,
            nfr_section=nfr_section,
        )
    except Exception as e:
        raise _llm_error_to_http(e)

    external_interfaces_section = clean_interface_diagrams(external_interfaces_section)


    image_paths = {
    'user_interfaces': Path(f'./srs_engine/static/{project_name}_user_interfaces_diagram.png'),
    'hardware_interfaces': Path(f'./srs_engine/static/{project_name}_hardware_interfaces_diagram.png'),
    'software_interfaces': Path(f'./srs_engine/static/{project_name}_software_interfaces_diagram.png'),
    'communication_interfaces': Path(f'./srs_engine/static/{project_name}_communication_interfaces_diagram.png')
}


    render_mermaid_png(external_interfaces_section['user_interfaces']['interface_diagram']['code'], image_paths['user_interfaces'])
    render_mermaid_png(external_interfaces_section['hardware_interfaces']['interface_diagram']['code'], image_paths['hardware_interfaces'])
    render_mermaid_png(external_interfaces_section['software_interfaces']['interface_diagram']['code'], image_paths['software_interfaces'])
    render_mermaid_png(external_interfaces_section['communication_interfaces']['interface_diagram']['code'], image_paths['communication_interfaces'])



    print("Non-Functional Requirements Section: ", nfr_section)


    print("Glossary Section: ", glossary_section)


    print("Assumptions Section: ", assumptions_section)


    ## SRS Making ##
    output_path = f"./srs_engine/generated_srs/{project_name}_SRS.docx"

    Path("./srs_engine/generated_srs").mkdir(exist_ok=True)

    generated_path = generate_srs_document(
        project_name=project_name,
        introduction_section=introduction_section,
        overall_description_section=overall_description_section,
        system_features_section=system_features_section,
        external_interfaces_section=external_interfaces_section,
        nfr_section=nfr_section,
        glossary_section=glossary_section,
        assumptions_section=assumptions_section,
        image_paths=image_paths,
        output_path=output_path,
        authors=author_list , # List of authors
        organization=organization_name
    )

    print(f"✅ SRS document generated successfully: {generated_path}")




    return {
        "srs_document_path": generated_path
    }





