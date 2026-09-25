<div align="center">

# 📖 StorySpark

### ✨ *Where Two AI Agents Write Stories Together* ✨

**A multi-agent children's story generator powered by CrewAI, Google Gemini and OWASP Top 10 LLM 2025 Security Framework.**

[![Live App](https://img.shields.io/badge/🚀_Live_App-storyspark9.streamlit.app-1e3a8a?style=for-the-badge)](https://storyspark9.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-FF6B6B?style=for-the-badge)](https://crewai.com)
[![Gemini](https://img.shields.io/badge/Gemini-Free_Tier-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![OWASP](https://img.shields.io/badge/OWASP-LLM_Top_10_2025-000000?style=for-the-badge&logo=owasp&logoColor=white)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

</div>

---

## 🌟 What Is StorySpark?

StorySpark is a **two-agent AI system** that collaborates to write short, warm children's stories on any theme — completely free, fully deployed, and hardened against real-world LLM security risks.

- 🧠 **Agent 1 (IdeaGenerator)** — finds one creative story idea using Wikipedia as a knowledge source.
- ✍️ **Agent 2 (StoryWriter)** — turns that idea into an 80-word tale.
- 🔄 **Agent Handoff** — Agent 1's output is stored in short-term memory and passed to Agent 2 as its input (sequential pipeline pattern).

---

## 🎬 Live Demo

🌐 **[storyspark9.streamlit.app](https://storyspark9.streamlit.app)**

Features: Live agent panels · Dark/Light mode · Chat history · Download stories

---

## 🏗️ Architecture

### Pipeline Flow

| Step | Stage | Description |
|:----:|-------|-------------|
| 1️⃣ | 🎯 **Streamlit UI** | User enters Theme + Age → clicks Run Agents |
| 2️⃣ | 🎬 **Orchestrator** | `run_storyspark_streaming()` coordinates the pipeline |
| 3️⃣ | 🧠 **Agent 1 — IdeaGenerator** | Uses Wikipedia tool · produces one sentence · retries once on failure |
| 4️⃣ | 💾 **Short-Term Memory** | `memory.save("idea", ...)` bridges Agent 1 to Agent 2 |
| 5️⃣ | ✍️ **Agent 2 — StoryWriter** | Reads idea from memory · writes 80-word story |
| 6️⃣ | 📝 **Final Output** | Story rendered in UI + saved to chat history |

### Component Breakdown

| Layer | Responsibility |
|-------|----------------|
| **Streamlit UI** | Captures theme + age, displays agent panels |
| **Orchestrator** | Coordinates retry logic and memory handoff |
| **Agent 1** | Uses Wikipedia as a free knowledge source to generate a story idea |
| **Short-Term Memory** | Bridges Agent 1 output to Agent 2 input |
| **Agent 2** | Consumes idea, writes children's story |
| **Output** | Rendered in UI + saved to chat history |

---

## ✨ Feature Highlights

### 🤖 Multi-Agent System
- Two CrewAI agents with distinct roles
- Sequential agent handoff via short-term memory
- Shared memory bridge between agents

### 🧠 Intelligent Pipeline
- Wikipedia API for grounded ideas
- Max 1 retry on failure
- Three-layer fallback safety

### 🎨 Beautiful UI
- Live agent process panels
- Dark / Light mode toggle
- Chat history with export

### 🔒 Security First
- OWASP Top 10 for LLM 2025
- Input validation before LLM
- English-only enforcement

---

## 🔐 OWASP Top 10 for LLM Applications 2025

StorySpark implements mitigations for the most critical LLM risks:

| Risk | Mitigation | File |
|------|-----------|------|
| **LLM01** · Prompt Injection | User input treated as data; validator blocks injection patterns | `crew.py` → `is_topic_valid()` |
| **LLM05** · Improper Output Handling | No HTML/JS/SQL in output; Streamlit renders plain text | `security_prompts.py` |
| **LLM07** · System Prompt Leakage | Prompts never revealed; verbose mode disabled | `security_prompts.py` |

**Defense Layers:**

1. **Input Validator** — Blocks unsafe patterns *before* LLM call
2. **System Prompt Directives** — English-only · No leakage · No HTML
3. **Output Detection** — Fallback text detection + UI warnings

---

## 🚀 Quick Start

### 📦 Installation

```bash
git clone https://github.com/daniyaliRiazcute-alt/StorySpark.git
cd StorySpark

python3.12 -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 🔑 Get a Free Gemini API Key

1. Visit [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with any Google account
3. Click **Create API key**
4. Copy the key (starts with `AIza...`)

### 🔧 Configure

**Streamlit Cloud:** Add to **Settings → Secrets**:

```toml
GEMINI_API_KEY = "AIzaSy..."
```

**Local:** Set an environment variable:

```bash
export GEMINI_API_KEY="AIzaSy..."
```

### ▶️ Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Project Structure

```
storyspark/
├── app.py                  # Streamlit UI + chat history + themes
├── crew.py                 # Two CrewAI agents + orchestrator
├── security_prompts.py     # OWASP 2025 system prompts
├── memory.py               # Short-term memory store
├── retry.py                # Max 1 retry logic
├── tools.py                # Wikipedia @tool (crewai.tools)
├── wikipedia_client.py     # Wikipedia API client
├── requirements.txt
├── runtime.txt             # python-3.12
├── README.md
└── .gitignore
```

---

## 🧪 Tested Themes
...
