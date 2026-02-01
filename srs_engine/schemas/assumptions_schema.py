from typing import List, Optional
from pydantic import BaseModel, ConfigDict , Field

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AssumptionItem(StrictBaseModel):
    description: str
    impact: str

class AssumptionsSection(StrictBaseModel):
    title: str

    assumptions: List[AssumptionItem]