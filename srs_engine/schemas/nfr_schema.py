from typing import List, Optional
from pydantic import BaseModel, ConfigDict , Field

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class NonFunctionalRequirement(StrictBaseModel):
    # Removing Optional and = None to force these into the JSON Schema 'required' array
    description: str
    rationale: str = Field(..., description="The technical or business justification for this requirement.")

class PerformanceRequirementsSection(StrictBaseModel):
    title: str
    requirements: List[NonFunctionalRequirement]

class SafetyRequirementsSection(StrictBaseModel):
    title: str
    requirements: List[NonFunctionalRequirement]


class SecurityRequirementsSection(StrictBaseModel):
    title: str
    requirements: List[NonFunctionalRequirement]


class QualityAttributesSection(StrictBaseModel):
    title: str
    requirements: List[NonFunctionalRequirement]

class NonFunctionalRequirementsSection(StrictBaseModel):
    title: str

    performance_requirements: PerformanceRequirementsSection
    safety_requirements: SafetyRequirementsSection
    security_requirements: SecurityRequirementsSection
    quality_attributes: QualityAttributesSection

