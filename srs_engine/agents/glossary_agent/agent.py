import os
from dotenv import load_dotenv, find_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .prompt import AGENT_DESCRIPTION , AGENT_INSTRUCTION
from ...schemas.glossary_schema import GlossaryResponse
from ...utils.globals import generate_content_config
from ...utils.model import *


# ==================================================
# Phase 3 System Design Agent ( for CLI )
# ==================================================

glossary_agent = LlmAgent(
    name="glossary_agent",
    model=groq_llm,
    output_schema=GlossaryResponse,
    description=AGENT_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    output_key="glossary_section",
    generate_content_config = generate_content_config
)


## For app

def create_glossary_agent():
    return LlmAgent(
    name="glossary_agent",
    model=groq_llm,
    output_schema=GlossaryResponse,
    description=AGENT_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    output_key="glossary_section",
    generate_content_config = generate_content_config
)
