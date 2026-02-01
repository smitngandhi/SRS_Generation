from typing import List
from pydantic import BaseModel, ConfigDict , Field

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class StimulusResponse(StrictBaseModel):
    stimulus: str
    response: str

class FunctionalRequirement(StrictBaseModel):
    description: str

class SystemFeature(StrictBaseModel):
    feature_name: str
    description: str
    stimulus_response: List[StimulusResponse]
    functional_requirements: List[FunctionalRequirement]

# --- ADD THIS WRAPPER CLASS ---
class SystemFeaturesSection(StrictBaseModel):
    title: str = Field(description="The title of the features section")  # Remove default
    features: List[SystemFeature]