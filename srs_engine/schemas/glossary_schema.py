from pydantic import BaseModel
from typing import List

from pydantic import BaseModel, ConfigDict , Field

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Term(StrictBaseModel):
    term: str
    definition: str

class GlossarySection(StrictBaseModel):
    title: str
    terms: List[Term]

class GlossaryResponse(StrictBaseModel):
    """Root model that wraps the array of sections"""
    sections: List[GlossarySection]