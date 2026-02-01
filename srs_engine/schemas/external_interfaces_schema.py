from typing import List, Optional
from pydantic import BaseModel, ConfigDict , Field

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class InterfaceDiagram(StrictBaseModel):
    diagram_type: str  # always "mermaid"
    code: str     


class UserInterfaceSection(StrictBaseModel):
    title: str
    description: str
    interface_diagram: InterfaceDiagram

class HardwareInterfaceSection(StrictBaseModel):
    title: str
    description: str
    interface_diagram: InterfaceDiagram

class SoftwareInterfaceSection(StrictBaseModel):
    title: str
    description: str
    interface_diagram: InterfaceDiagram

class CommunicationInterfaceSection(StrictBaseModel):
    title: str
    description: str
    interface_diagram: InterfaceDiagram

class ExternalInterfacesSection(StrictBaseModel):
    title: str

    user_interfaces: UserInterfaceSection
    hardware_interfaces: HardwareInterfaceSection
    software_interfaces: SoftwareInterfaceSection
    communication_interfaces: CommunicationInterfaceSection