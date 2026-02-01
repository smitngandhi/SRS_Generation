from typing import List, Optional
from pydantic import BaseModel, ConfigDict , Field

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class ProductPerspectiveSection(StrictBaseModel):
    title: str
    description: str

class ProductFeaturesSection(StrictBaseModel):
    title: str
    features: List[str]

class UserClassCharacteristic(StrictBaseModel):
    user_class: str
    characteristics: List[str]

class UserClassesAndCharacteristicsSection(StrictBaseModel):
    title: str
    user_classes: List[UserClassCharacteristic]


class OperatingEnvironmentSection(StrictBaseModel):
    title: str
    environments: List[str]


class DesignAndImplementationConstraintsSection(StrictBaseModel):
    title: str
    constraints: List[str]


class UserDocumentationSection(StrictBaseModel):
    title: str
    documents: List[str]



class AssumptionsAndDependenciesSection(StrictBaseModel):
    title: str
    assumptions: List[str]
    dependencies: List[str]


class OverallDescriptionSection(StrictBaseModel):
    title: str

    product_perspective: ProductPerspectiveSection
    product_features: ProductFeaturesSection
    user_classes_and_characteristics: UserClassesAndCharacteristicsSection
    operating_environment: OperatingEnvironmentSection
    design_and_implementation_constraints: DesignAndImplementationConstraintsSection
    user_documentation: UserDocumentationSection
    assumptions_and_dependencies: AssumptionsAndDependenciesSection



