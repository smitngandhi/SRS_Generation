import os
from dotenv import load_dotenv, find_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .prompt import AGENT_DESCRIPTION, AGENT_INSTRUCTION
from ...schemas.section_enhancement_schema import EnhancedSectionOutput
from ...utils.globals import generate_content_config
from ...utils.llm_config import get_configured_model

load_dotenv(find_dotenv())

MODEL = get_configured_model()

llm = LiteLlm(model=MODEL)


def create_section_enhancer_agent() -> LlmAgent:
    return LlmAgent(
        name="section_enhancer_agent",
        model=llm,
        output_schema=EnhancedSectionOutput,
        description=AGENT_DESCRIPTION,
        instruction=AGENT_INSTRUCTION,
        output_key="enhanced_section",
        generate_content_config=generate_content_config,
    )
