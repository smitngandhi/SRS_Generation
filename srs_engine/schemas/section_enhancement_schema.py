from pydantic import BaseModel, Field, validator
from typing import Literal


SectionType = Literal["Problem Statement", "Core Features", "Primary User Flow"]


class SectionEnhancementRequest(BaseModel):
    section_type: SectionType = Field(..., description="Which SRS section to enhance")
    user_input: str = Field(..., description="Raw user-provided text to enhance")

    @validator("user_input")
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("user_input cannot be empty")
        return v.strip()


class SectionEnhancementResponse(BaseModel):
    content: str = Field(..., description="Enhanced SRS-ready content")


class EnhancedSectionOutput(BaseModel):
    content: str = Field(
        ...,
        description=(
            "Enhanced SRS-ready content only. No headings, no explanations, no code fences. "
            "Must follow the formatting rules for the requested section."
        ),
    )

    @validator("content")
    def content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v.strip()

