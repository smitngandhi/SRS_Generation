Here is your setup guide formatted as a clean, professional README.md style document.

🚀 SRS Generation System Setup
Follow these steps to get the environment ready for generating Software Requirements Specifications.

📋 Prerequisites
Python 3.10+

Node.js (Latest LTS version recommended)

Groq API Key

🛠 Installation Steps
1. Clone the Repository
Bash
git clone https://github.com/smitngandhi/SRS_Generation.git
cd SRS_generation
2. Python Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.

Bash
# Create the environment
python -m venv venv

# Activate the environment (Windows)
venv\Scripts\activate

# Activate the environment (Mac/Linux)
source venv/bin/activate
3. Diagram Rendering Support (Mermaid)
The system uses Mermaid to generate architecture diagrams. You must install the CLI tool globally via npm.

Install Mermaid CLI:

Bash
npm install -g @mermaid-js/mermaid-cli
Locate the CMD path: Note your local path for configuration (usually required in your settings or .env): C:/Users/<Your Username>/AppData/Roaming/npm/mmdc.cmd

⚙️ Configuration
Environment Variables
Create a file named .env in the root directory of the project and populate it with the following:

Ini, TOML
# API Credentials
GROQ_API_KEY=your_actual_api_key_here

# Model Configuration
GROQ_MODEL=groq/meta-llama/llama-4-scout-17b-16e-instruct
🏗 System Architecture
The following diagram illustrates how your local setup interacts with the Groq API and Mermaid CLI.

📝 Usage Note
Make sure your virtual environment is activated whenever you run the FastAPI server or the generation scripts. If you encounter a mmdc error, ensure that Node.js is correctly added to your system's PATH.

Would you like me to generate a requirements.txt file content based on the Python code you've shared so far?