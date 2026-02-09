import os
from google.adk.agents import LlmAgent
from .prompt import AGENT_DESCRIPTION , AGENT_INSTRUCTION
from ....schemas.external_interfaces_schema import ExternalInterfacesSection
from ....utils.globals import generate_content_config
from ....utils.model import *

# ==================================================
# Phase 3 System Design Agent ( for CLI )
# ==================================================

external_interfaces_agent = LlmAgent(
    name="external_interfaces_agent",
    model=groq_llm,
    output_schema=ExternalInterfacesSection,
    description=AGENT_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    output_key="external_interfaces_section",
    generate_content_config = generate_content_config
)


## For app

def create_external_interfaces_agent():
    return LlmAgent(
    name="external_interfaces_agent",
    model=groq_llm,
    output_schema=ExternalInterfacesSection,
    description=AGENT_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    output_key="external_interfaces_section",
    generate_content_config = generate_content_config
)
