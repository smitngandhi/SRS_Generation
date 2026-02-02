# 🚀 SRS Generation System


**AI-powered automated Software Requirements Specification (SRS) document generator with architecture diagrams**

---

## 🎯 Overview

An intelligent multi-agent system that automates SRS creation using **Groq's free API**. Built with FastAPI, it generates professional IEEE 830-1998 compliant documents complete with Mermaid diagrams - all in minutes!

**Key Features:**
- 🤖 7 Specialized AI agents for different SRS sections
- ⚡ Powered by Groq's lightning-fast LLM inference
- 📄 Professional `.docx` output with architecture diagrams
- 🆓 100% Free - No billing required
- 🔒 Runs locally - Your data stays private

---

## 📦 Prerequisites

| Requirement | Version | Download |
|------------|---------|----------|
| Python | 3.10+ | [Download](https://www.python.org/downloads/) |
| Node.js | Latest LTS | [Download](https://nodejs.org/) |
| Git | Latest | [Download](https://git-scm.com/downloads/) |
| Groq API Key | Free | [Get Key](https://console.groq.com/keys) |

---

## 🛠 Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/smitngandhi/SRS_Generation.git
cd SRS_Generation
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> 💡 You'll see `(venv)` in your terminal when activated

### Step 3: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install Mermaid CLI
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc --version  # Verify installation
```

> **⚠️ CRITICAL for Windows Users**: After installation, you **MUST** configure the Mermaid CLI path in the code.

**Windows Configuration:**
1. Locate your Mermaid CLI installation path (typically):
   ```
   C:\Users\<Your Username>\AppData\Roaming\npm\mmdc.cmd
   ```

2. Open `srs_engine/utils/globals.py` and update the `render_mermaid_png` function:
   ```python
   # Find the subprocess.run line and update it to:
   subprocess.run([
       "C:\\Users\\<Your Username>\\AppData\\Roaming\\npm\\mmdc.cmd",
       "-i", str(mmd_path),
       "-o", str(output_path)
   ], check=True)
   ```

3. Replace `<Your Username>` with your actual Windows username

**Without this configuration, diagram generation will fail on Windows!**

---

## ⚙️ Configuration

### 1. Get Your Free Groq API Key
1. Visit [console.groq.com/keys](https://console.groq.com/keys)
2. Sign up (no billing required!)
3. Create API Key
4. Copy your key

### 2. Create `.env` File

**Windows:**
```bash
type nul > .env
```

**macOS/Linux:**
```bash
touch .env
```

### 3. Add Configuration

Open `.env` and add:

```ini
# Groq API Key (Required)
GROQ_API_KEY=your_actual_api_key_here

# Model Selection (Required)
GROQ_MODEL=groq/meta-llama/llama-4-scout-17b-16e-instruct
```

**Available Models:** [Groq Models Docs](https://console.groq.com/docs/models)

| Model | Format | Best For |
|-------|--------|----------|
| Llama 4 Scout 17B | `groq/meta-llama/llama-4-scout-17b-16e-instruct` | ⭐ Recommended |
| Llama 3.3 70B | `groq/meta-llama/llama-3.3-70b-versatile` | High Quality |
| Llama 3.1 8B | `groq/meta-llama/llama-3.1-8b-instant` | Fast Speed |

---

## 🚀 Usage

### 1. Start Server
```bash
uvicorn srs_engine.main:app --reload
```

### 2. Open Web Interface
Navigate to: **http://127.0.0.1:8000**

### 3. Enter Project Details
Fill in the form:
- Project Name
- Project Description
- Key Features
- Target Users
- Technology Stack (optional)

### 4. Generate SRS
Click "Generate SRS" and wait 2-5 minutes

### 5. Access Generated Files

**SRS Document:**
```
srs_engine/generated_srs/{project_name}_SRS.docx
```

**Architecture Diagrams:**
```
srs_engine/static/{project_name}_user_interfaces_diagram.png
srs_engine/static/{project_name}_hardware_interfaces_diagram.png
srs_engine/static/{project_name}_software_interfaces_diagram.png
srs_engine/static/{project_name}_communication_interfaces_diagram.png
```

---

## 🔧 Troubleshooting

**`mmdc: command not found`**
```bash
npm install -g @mermaid-js/mermaid-cli
# Add Node.js to PATH if needed
```

**`ModuleNotFoundError`**
```bash
# Activate venv first!
pip install -r requirements.txt
```

**API Key Error (401)**
- Verify key at [console.groq.com/keys](https://console.groq.com/keys)
- Check `.env` is in root directory
- No spaces/quotes around the key

**Port 8000 in use**
```bash
uvicorn srs_engine.main:app --reload --port 8001
```

**Diagrams not generating (Windows)**
```bash
# ⚠️ CRITICAL: Windows users must configure mmdc path
# Open srs_engine/utils/globals.py
# Find render_mermaid_png function and update subprocess.run to:

subprocess.run([
    "C:\\Users\\<Your Username>\\AppData\\Roaming\\npm\\mmdc.cmd",
    "-i", str(mmd_path),
    "-o", str(output_path)
], check=True)

# Replace <Your Username> with your actual Windows username
# Without this, mmdc won't be found even if installed correctly
```

---

## 📁 Project Structure

```
SRS_Generation/
├── srs_engine/
│   ├── agents/              # 7 specialized AI agents
│   ├── schemas/             # Pydantic models
│   ├── utils/               # Document generator
│   ├── templates/           # Web interface
│   ├── static/              # Generated diagrams
│   ├── generated_srs/       # Output documents
│   └── main.py              # FastAPI app
├── .env                     # Your configuration
├── requirements.txt         # Dependencies
└── README.md
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/name`)
5. Open Pull Request

---


## 🙏 Acknowledgments

Built with: [FastAPI](https://fastapi.tiangolo.com/) • [Groq](https://groq.com/) • [Mermaid](https://mermaid.js.org/) • [python-docx](https://python-docx.readthedocs.io/)

---

<div align="center">

**Made with ❤️ by [Smit Gandhi](https://github.com/smitngandhi)**

⭐ Star this repo if you find it helpful!

[Report Bug](https://github.com/smitngandhi/SRS_Generation/issues) • [Request Feature](https://github.com/smitngandhi/SRS_Generation/issues)

</div>