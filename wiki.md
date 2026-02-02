# 📚 SRS Generation System - Technical Wiki

> **Complete technical documentation covering architecture, data flow, and implementation details**

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Data Flow](#data-flow)
4. [Multi-Agent System](#multi-agent-system)
5. [Agent Specifications](#agent-specifications)
6. [API Documentation](#api-documentation)
7. [Schema Definitions](#schema-definitions)
8. [Document Generation](#document-generation)
9. [Session Management](#session-management)
10. [Development Guide](#development-guide)

---

## System Architecture

### High-Level Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (Web UI)                      │
│         HTML Form → JavaScript Validation → POST          │
└─────────────────────────┬────────────────────────────────┘
                          │ /generate_srs
                          ▼
┌──────────────────────────────────────────────────────────┐
│                  FastAPI Backend (main.py)                │
│  • Pydantic Validation  • Session Creation  • Routing    │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│              Agent Orchestration Layer (ADK)              │
│                                                            │
│  ┌──────────── First Sequential Agent ─────────────┐     │
│  │  Parallel: 5 Agents (Introduction, Overall,     │     │
│  │             Features, Interfaces, NFR)           │     │
│  └──────────────────────┬───────────────────────────┘     │
│                         │ 20s delay                       │
│  ┌──────────── Second Sequential Agent ────────────┐     │
│  │  Parallel: 2 Agents (Glossary, Assumptions)     │     │
│  └──────────────────────────────────────────────────┘     │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│                   Groq API (LLM Layer)                    │
│        Llama 4 Scout 17B • Fast Inference • JSON          │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│              Document & Diagram Generation                │
│  • Mermaid CLI (PNG from .mmd)  • python-docx (DOCX)    │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│                    Output Files                           │
│  generated_srs/{project}_SRS.docx                        │
│  static/{project}_*_diagram.png/.mmd                     │
└──────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Frontend** | User input collection & validation | HTML5, Vanilla JS, CSS |
| **API Layer** | Request handling & routing | FastAPI, Uvicorn |
| **Validation** | Schema validation & type checking | Pydantic |
| **Orchestration** | Multi-agent coordination | Google ADK |
| **AI Layer** | Content generation | Groq API + Llama |
| **Document Gen** | DOCX creation | python-docx |
| **Diagram Gen** | Visual diagrams | Mermaid CLI |

---

## Technology Stack

### Core Dependencies

```python
# requirements.txt (key packages)
fastapi>=0.100.0           # Web framework
uvicorn>=0.23.0            # ASGI server
pydantic>=2.0.0            # Data validation
python-dotenv>=1.0.0       # Environment management
python-docx>=0.8.11        # Document generation
groq>=0.4.0                # Groq API client
google-adk>=1.0.0          # Agent orchestration
```

### External Tools

- **Node.js**: Required for Mermaid CLI
- **@mermaid-js/mermaid-cli**: Diagram rendering (`npm install -g`)
- **Groq API**: Free LLM inference (no billing required)

---

## Data Flow

### Complete Request Lifecycle

```
1. USER INPUT (Frontend)
   │
   ├─► Form validation (JavaScript)
   ├─► Data transformation (arrays, booleans)
   └─► POST /generate_srs (JSON payload)
   
2. REQUEST HANDLING (FastAPI)
   │
   ├─► Pydantic schema validation (SRSRequest)
   ├─► Extract project metadata (name, authors, org)
   └─► Generate UUID session_id
   
3. SESSION INITIALIZATION
   │
   ├─► Create session (InMemorySessionService)
   ├─► Set initial state: { "user_inputs": {...} }
   └─► Link session_id → project_name → user_id
   
4. FIRST AGENT WAVE (Parallel Execution)
   │
   ├─► Introduction Agent    ──┐
   ├─► Overall Desc Agent    ──┤
   ├─► System Features Agent ──┤→ Run simultaneously
   ├─► External Interfaces   ──┤   (3-4 minutes)
   └─► NFR Agent             ──┘
   │
   └─► Session state updated with 5 sections
   
5. INTER-WAVE DELAY
   │
   └─► time.sleep(20)  # API rate limiting
   
6. SECOND AGENT WAVE (Parallel Execution)
   │
   ├─► Glossary Agent      ──┐
   └─► Assumptions Agent   ──┘→ Run simultaneously
   │
   └─► Session state updated with 2 final sections
   
7. DATA EXTRACTION
   │
   ├─► Extract all 7 sections from session.state
   ├─► Parse JSON strings → Python dicts
   ├─► Clean Mermaid diagram code (remove ```)
   └─► Validate data structures
   
8. DIAGRAM GENERATION
   │
   ├─► Extract 4 Mermaid codes from external_interfaces
   ├─► Write .mmd files to static/
   ├─► Execute: mmdc -i input.mmd -o output.png
   └─► Generate 4 PNG images
   
9. DOCUMENT ASSEMBLY
   │
   ├─► Initialize python-docx Document
   ├─► Add title page (project, org, authors, date)
   ├─► Add sections in IEEE 830-1998 order
   ├─► Embed 4 diagram images
   ├─► Apply professional styling (Arial, tables)
   └─► Save: {project_name}_SRS.docx
   
10. RESPONSE
    │
    └─► Return { "srs_document_path": "..." }
```

### Session State Evolution

**Initial State:**
```json
{
  "user_inputs": {
    "project_identity": {...},
    "system_context": {...},
    "functional_scope": {...},
    "non_functional_requirements": {...},
    "security_and_compliance": {...},
    "technical_preferences": {...},
    "output_control": {...}
  }
}
```

**After First Wave:**
```json
{
  "user_inputs": {...},
  "introduction_section": "{...JSON string...}",
  "overall_description_section": "{...JSON string...}",
  "system_features_section": "{...JSON string...}",
  "external_interfaces_section": "{...JSON string...}",
  "nfr_section": "{...JSON string...}"
}
```

**After Second Wave (Final):**
```json
{
  // ... all previous sections ...
  "glossary_section": "{...JSON string...}",
  "assumptions_section": "{...JSON string...}"
}
```

---

## Multi-Agent System

### Agent Hierarchy

```python
Root
│
├─► First Sequential Agent
│   └─► First Parallel Agent
│       ├─► Introduction Agent
│       ├─► Overall Description Agent
│       ├─► System Features Agent
│       ├─► External Interfaces Agent
│       └─► NFR Agent
│
└─► Second Sequential Agent (after 20s delay)
    └─► Second Parallel Agent
        ├─► Glossary Agent
        └─► Assumptions Agent
```

### Why This Architecture?

**Parallel Execution Benefits:**
- 5 independent agents run simultaneously
- Reduces total time from ~15 min to ~4 min
- Each agent writes to unique session state key (no conflicts)

**Sequential Dependencies:**
- Glossary needs all terminology from previous sections
- Assumptions need complete system context
- 20-second delay ensures base content is complete

**Session State Sharing:**
- All agents read from shared `session.state`
- Each agent writes to its own key: `{agent_name}_section`
- Later agents reference earlier outputs for consistency

### Implementation

```python
async def create_srs_agent():
    first_agent = SequentialAgent(
        name="first_agent",
        sub_agents=[
            ParallelAgent(
                name="first_parallel_agent",
                sub_agents=[
                    create_introduction_agent(),
                    create_overall_description_agent(),
                    create_system_features_agent(),
                    create_external_interfaces_agent(),
                    create_nfr_agent()
                ]
            )
        ]
    )
    
    second_agent = SequentialAgent(
        name="second_agent",
        sub_agents=[
            ParallelAgent(
                name="finalization_agent",
                sub_agents=[
                    create_glossary_agent(),
                    create_assumptions_agent()
                ]
            )
        ]
    )
    
    return first_agent, second_agent
```

---

## Agent Specifications

### 1. Introduction Agent

**Output Key:** `introduction_section`

**Structure:**
```json
{
  "purpose": "string",
  "document_conventions": "string",
  "intended_audience": ["string"],
  "project_scope": "string",
  "references": [
    {"title": "string", "url": "string", "description": "string"}
  ]
}
```

### 2. Overall Description Agent

**Output Key:** `overall_description_section`

**Structure:**
```json
{
  "product_perspective": "string",
  "product_features": ["string"],
  "user_classes": [
    {"class": "string", "characteristics": "string"}
  ],
  "operating_environment": "string",
  "constraints": ["string"],
  "assumptions_dependencies": ["string"]
}
```

### 3. System Features Agent

**Output Key:** `system_features_section`

**Structure:**
```json
{
  "features": [
    {
      "id": "F1",
      "name": "string",
      "priority": "High|Medium|Low",
      "description": "string",
      "requirements": [
        {"id": "F1.1", "description": "string"}
      ]
    }
  ]
}
```

### 4. External Interfaces Agent

**Output Key:** `external_interfaces_section`

**Structure:**
```json
{
  "user_interfaces": {
    "description": "string",
    "interface_diagram": {
      "type": "mermaid",
      "code": "graph TD\nA-->B"
    },
    "components": ["string"]
  },
  "hardware_interfaces": {...},
  "software_interfaces": {
    "description": "string",
    "interface_diagram": {...},
    "interfaces": [
      {"name": "string", "purpose": "string", "protocol": "string"}
    ]
  },
  "communication_interfaces": {...}
}
```

### 5. NFR Agent

**Output Key:** `nfr_section`

**Structure:**
```json
{
  "performance_requirements": [
    {"id": "P1", "description": "string"}
  ],
  "safety_requirements": [
    {"id": "S1", "description": "string"}
  ],
  "security_requirements": [
    {"id": "SEC1", "description": "string"}
  ],
  "quality_attributes": [
    {"attribute": "Reliability", "description": "string"}
  ]
}
```

### 6. Glossary Agent

**Output Key:** `glossary_section`

**Dependencies:** Reads all previous sections

**Structure:**
```json
{
  "terms": [
    {"term": "API", "definition": "Application Programming Interface"}
  ]
}
```

### 7. Assumptions Agent

**Output Key:** `assumptions_section`

**Dependencies:** Reads all previous sections

**Structure:**
```json
{
  "assumptions": [
    {"id": "A1", "description": "string"}
  ],
  "dependencies": [
    {"id": "D1", "description": "string"}
  ]
}
```

---

## API Documentation

### GET /

**Description:** Serve web interface

**Response:** HTML page

**Status:** 200 OK

---

### POST /generate_srs

**Description:** Generate complete SRS document

**Request Body:**
```json
{
  "project_identity": {
    "project_name": "string",
    "author": ["string"],
    "organization": "string",
    "problem_statement": "string",
    "target_users": ["Admin", "End User"]
  },
  "system_context": {
    "application_type": "Web Application",
    "domain": "Finance"
  },
  "functional_scope": {
    "core_features": ["Feature 1", "Feature 2"],
    "primary_user_flow": "string (optional)"
  },
  "non_functional_requirements": {
    "expected_user_scale": "<100|100-1k|1k-100k|>100k",
    "performance_expectation": "Normal|High|Real-time"
  },
  "security_and_compliance": {
    "authentication_required": true,
    "sensitive_data_handling": false,
    "compliance_requirements": ["GDPR", "HIPAA"]
  },
  "technical_preferences": {
    "preferred_backend": "Python (optional)",
    "database_preference": "SQL (optional)",
    "deployment_preference": "Cloud (optional)"
  },
  "output_control": {
    "srs_detail_level": "High-level|Technical|Enterprise-grade"
  }
}
```

**Response:**
```json
{
  "srs_document_path": "./srs_engine/generated_srs/ProjectName_SRS.docx"
}
```

**Status Codes:**
- 200: Success
- 422: Validation Error
- 500: Internal Server Error

**Processing Time:** 3-5 minutes

---

## Schema Definitions

### Input Schema (Pydantic)

```python
from pydantic import BaseModel
from typing import List, Optional

class ProjectIdentity(BaseModel):
    project_name: str
    author: List[str]  # Min: 1 author
    organization: str
    problem_statement: str
    target_users: List[str]  # Min: 1 user

class SRSRequest(BaseModel):
    project_identity: ProjectIdentity
    system_context: SystemContext
    functional_scope: FunctionalScope
    non_functional_requirements: NonFunctionalRequirements
    security_and_compliance: SecurityAndCompliance
    technical_preferences: TechnicalPreferences
    output_control: OutputControl
```

### Validation Rules

- **project_name**: Non-empty, used for file naming (no special chars)
- **author**: List with at least 1 name
- **target_users**: List with at least 1 selection
- **core_features**: List with at least 1 feature
- **authentication_required**: Boolean required
- **srs_detail_level**: Enum validation

---

## Document Generation

### IEEE 830-1998 Structure

```
1. Title Page
   • Project Name
   • Organization
   • Authors (list)
   • Date
   • Version 1.0

2. Table of Contents (auto-generated)

3. Introduction
   3.1 Purpose
   3.2 Document Conventions
   3.3 Intended Audience
   3.4 Project Scope
   3.5 References

4. Overall Description
   4.1 Product Perspective
   4.2 Product Features
   4.3 User Classes
   4.4 Operating Environment
   4.5 Constraints
   4.6 Assumptions

5. System Features
   5.1 Feature 1
       • Description
       • Priority
       • Requirements (F1.1, F1.2, ...)

6. External Interfaces
   6.1 User Interfaces
       • [Embedded PNG Diagram]
   6.2 Hardware Interfaces
       • [Embedded PNG Diagram]
   6.3 Software Interfaces
       • [Embedded PNG Diagram]
   6.4 Communication Interfaces
       • [Embedded PNG Diagram]

7. Non-Functional Requirements
   7.1 Performance
   7.2 Safety
   7.3 Security
   7.4 Quality Attributes

8. Other Requirements
   8.1 Glossary
   8.2 Assumptions & Dependencies
```

### Styling Guidelines

- **Font:** Arial 11pt (body), 16pt/14pt/12pt (H1/H2/H3)
- **Page:** US Letter, 1" margins
- **Lists:** Proper numbering (not unicode bullets)
- **Tables:** Gray headers (#D5E8F0), 1pt borders
- **Images:** Max 6" width, embedded inline

### Diagram Rendering

```python
def render_mermaid_png(mermaid_code: str, output_path: Path):
    """
    1. Clean code (remove ```mermaid fences)
    2. Write to .mmd file
    3. Execute: mmdc -i input.mmd -o output.png
    4. Verify PNG exists
    """
    mmd_path = output_path.with_suffix('.mmd')
    mmd_path.write_text(mermaid_code)
    subprocess.run(['mmdc', '-i', str(mmd_path), '-o', str(output_path)])
```

---

## Session Management

### InMemorySessionService

**Purpose:** Temporary state storage during agent execution

**Lifecycle:**
```python
1. create_session(service, project, user, session_id, initial_state)
   └─► Creates in-memory session object

2. Agents read/write via session.state during execution
   └─► Each agent updates its own key

3. get_session(service, project, user, session_id)
   └─► Retrieve final state with all sections

4. Session discarded after document generation
   └─► No persistence (in-memory only)
```

**Key Methods:**
```python
# Create
await create_session(session_service, project_name, user_id, session_id, initial_state)

# Retrieve
session = await get_session(session_service, project_name, user_id, session_id)

# Access state
introduction = session.state.get("introduction_section")
```

---

## Development Guide

### Adding a New Agent

**1. Create Agent Directory:**
```
srs_engine/agents/new_agent/
├── __init__.py
├── agent.py
└── prompt.py
```

**2. Implement agent.py:**
```python
from google.adk.agents import Agent

def create_new_agent():
    return Agent(
        name="new_agent",
        description="Agent description",
        prompt_path="srs_engine/agents/new_agent/prompt.py",
        output_key="new_section"
    )
```

**3. Create prompt.py:**
```python
def get_prompt(state):
    user_inputs = state.get("user_inputs", {})
    return f"""
    Generate section based on: {user_inputs}
    
    Output JSON:
    {{
        "field1": "value",
        "field2": ["list"]
    }}
    """
```

**4. Add to Orchestration:**
```python
# In main.py
ParallelAgent(
    sub_agents=[
        existing_agents...,
        create_new_agent()
    ]
)
```

**5. Update Document Generator:**
```python
# In srs_document_generator.py
new_section = clean_and_parse_json(session.state.get("new_section", {}))
# Add to document
```

### Local Testing

```bash
# Activate venv
source venv/bin/activate  # or venv\Scripts\activate (Windows)

# Run server
uvicorn srs_engine.main:app --reload

# Test endpoint
curl -X POST http://localhost:8000/generate_srs \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

### Environment Configuration

```bash
# .env file
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
GROQ_MODEL=groq/meta-llama/llama-4-scout-17b-16e-instruct
```

---

## Performance Notes

- **Total Time:** ~1-2 minutes per SRS
- **Parallelization:** Reduces from 2-3 min (sequential) to 1 min
- **Rate Limiting:** 20s delay prevents Groq API throttling
- **Bottleneck:** LLM inference (mitigated by parallel execution)

---

## Future Enhancements

- [ ] Add retry logic for failed agent executions
- [ ] Implement caching for common terms
- [ ] Add real-time progress updates (WebSocket)
- [ ] Support for custom templates
- [ ] Export to PDF format
- [ ] Batch processing for multiple projects

---

**Last Updated:** February 2026  
**Version:** 1.0.0  
**Maintainer:** Smit Gandhi