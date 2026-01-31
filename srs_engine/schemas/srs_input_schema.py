from pydantic import BaseModel, Field, validator
from typing import List, Optional


class ProjectIdentity(BaseModel):
    """Project identification and basic information"""
    project_name: str = Field(..., description="Name of the project")
    problem_statement: str = Field(..., description="Problem this system is intended to solve")
    target_users: List[str] = Field(..., min_items=1, description="Primary users of the system")
    
    @validator('project_name', 'problem_statement')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @validator('target_users')
    def validate_target_users(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one target user must be selected')
        return v


class SystemContext(BaseModel):
    """System context and domain information"""
    application_type: str = Field(..., description="Type of application being built")
    domain: str = Field(..., description="Domain or industry of the system")
    
    @validator('application_type', 'domain')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()


class FunctionalScope(BaseModel):
    """Functional requirements and capabilities"""
    core_features: List[str] = Field(..., min_items=1, description="Core features or capabilities of the system")
    primary_user_flow: Optional[str] = Field(None, description="Primary user journey through the system")
    
    @validator('core_features')
    def validate_core_features(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one core feature must be provided')
        # Remove empty strings
        return [feature.strip() for feature in v if feature.strip()]
    
    @validator('primary_user_flow')
    def strip_user_flow(cls, v):
        if v:
            return v.strip()
        return v


class NonFunctionalRequirements(BaseModel):
    """Non-functional requirements"""
    expected_user_scale: str = Field(..., description="Expected number of users")
    performance_expectation: str = Field(..., description="Expected performance level")
    
    @validator('expected_user_scale')
    def validate_user_scale(cls, v):
        valid_scales = ["<100", "100-1k", "1k-100k", ">100k"]
        if v not in valid_scales:
            raise ValueError(f'User scale must be one of {valid_scales}')
        return v
    
    @validator('performance_expectation')
    def validate_performance(cls, v):
        valid_performance = ["Normal", "High", "Real-time"]
        if v not in valid_performance:
            raise ValueError(f'Performance expectation must be one of {valid_performance}')
        return v


class SecurityAndCompliance(BaseModel):
    """Security and compliance requirements"""
    authentication_required: bool = Field(..., description="Whether user authentication is required")
    sensitive_data_handling: bool = Field(..., description="Whether system handles sensitive or personal data")
    compliance_requirements: Optional[List[str]] = Field(
        default_factory=list, 
        description="Compliance requirements (GDPR, HIPAA, etc.)"
    )
    
    @validator('compliance_requirements')
    def validate_compliance(cls, v):
        if v is None:
            return []
        # Remove empty strings
        return [req.strip() for req in v if req.strip()]


class TechnicalPreferences(BaseModel):
    """Technical stack preferences"""
    preferred_backend: Optional[str] = Field(None, description="Preferred backend technology")
    database_preference: Optional[str] = Field(None, description="Database preference")
    deployment_preference: Optional[str] = Field(None, description="Deployment preference")
    
    @validator('preferred_backend', 'database_preference', 'deployment_preference')
    def strip_if_exists(cls, v):
        if v:
            stripped = v.strip()
            return stripped if stripped else None
        return v


class OutputControl(BaseModel):
    """Output generation control"""
    srs_detail_level: str = Field(..., description="Detail level for the generated SRS")
    
    @validator('srs_detail_level')
    def validate_detail_level(cls, v):
        valid_levels = ["High-level", "Technical", "Enterprise-grade"]
        if v not in valid_levels:
            raise ValueError(f'Detail level must be one of {valid_levels}')
        return v


class SRSRequest(BaseModel):
    """Complete SRS generation request"""
    project_identity: ProjectIdentity
    system_context: SystemContext
    functional_scope: FunctionalScope
    non_functional_requirements: NonFunctionalRequirements
    security_and_compliance: SecurityAndCompliance
    technical_preferences: TechnicalPreferences
    output_control: OutputControl
    
    class Config:
        schema_extra = {
            "example": {
                "project_identity": {
                    "project_name": "Customer Churn Prediction System",
                    "problem_statement": "Predict customers likely to leave the service to reduce churn",
                    "target_users": ["Admin", "Analyst", "Manager"]
                },
                "system_context": {
                    "application_type": "Web Application",
                    "domain": "Telecom"
                },
                "functional_scope": {
                    "core_features": [
                        "User authentication",
                        "Dashboard analytics",
                        "Data upload",
                        "Prediction engine",
                        "Report generation"
                    ],
                    "primary_user_flow": "User logs in, uploads customer data, views churn predictions, generates reports"
                },
                "non_functional_requirements": {
                    "expected_user_scale": "100-1k",
                    "performance_expectation": "High"
                },
                "security_and_compliance": {
                    "authentication_required": True,
                    "sensitive_data_handling": True,
                    "compliance_requirements": ["GDPR"]
                },
                "technical_preferences": {
                    "preferred_backend": "Python",
                    "database_preference": "SQL",
                    "deployment_preference": "Cloud"
                },
                "output_control": {
                    "srs_detail_level": "Technical"
                }
            }
        }


class SRSResponse(BaseModel):
    """Response after SRS generation"""
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Generated SRS data")
    srs_document: Optional[str] = Field(None, description="Generated SRS document content")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "SRS generated successfully",
                "data": {
                    "project_name": "Customer Churn Prediction System",
                    "generated_at": "2024-01-31T10:30:00"
                },
                "srs_document": "# Software Requirements Specification\n\n## 1. Introduction\n..."
            }
        }