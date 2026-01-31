from typing import List, Optional
from pydantic import BaseModel, ConfigDict , Field

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class PurposeSection(StrictBaseModel):
    title: str
    description: str

class DocumentConventionsSection(StrictBaseModel):
    title: str
    conventions: List[str]

class DefinitionItem(StrictBaseModel):
    term: str
    definition: str

class DefinitionsSection(StrictBaseModel):
    title: str
    items: List[DefinitionItem]

class IntendedAudienceSection(StrictBaseModel):
    title: str
    audience_groups: List[str]

class ProjectScopeSection(StrictBaseModel):
    title: str
    included: List[str]
    excluded: List[str]

class ReferenceItem(StrictBaseModel):
    id: str
    description: str

class ReferencesSection(StrictBaseModel):
    title: str
    references: List[ReferenceItem]

class IntroductionSection(StrictBaseModel):
    title: str
    purpose: PurposeSection
    intended_audience: IntendedAudienceSection
    project_scope: ProjectScopeSection
    definitions: Optional[DefinitionsSection] = Field(..., description="Project definitions")
    document_conventions: Optional[DocumentConventionsSection] = Field(..., description="Document conventions")
    references: ReferencesSection