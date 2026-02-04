import os
from dotenv import load_dotenv, find_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from srs_engine.schemas.glossary_schema import GlossarySection
from .prompt import AGENT_DESCRIPTION , AGENT_INSTRUCTION
from ...schemas.assumptions_schema import AssumptionsSection
from ...utils.globals import generate_content_config
from ...utils.llm_config import get_configured_model


load_dotenv(find_dotenv())

MODEL = get_configured_model()

llm = LiteLlm(model=MODEL)


# ==================================================
# Phase 3 System Design Agent ( for CLI )
# ==================================================

assumptions_agent = LlmAgent(
    name="assumptions_agent",
    model=llm,
    output_schema=AssumptionsSection,
    description=AGENT_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    output_key="assumptions_section",
    generate_content_config = generate_content_config
)


## For app

def create_assumptions_agent():
    return LlmAgent(
    name="assumptions_agent",
    model=llm,
    output_schema=AssumptionsSection,
    description=AGENT_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    output_key="assumptions_section",
    generate_content_config = generate_content_config
)
