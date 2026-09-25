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

- 🧠 **Agent 1 (IdeaGenerator)** — finds one creative story idea.
- ✍️ **Agent 2 (StoryWriter)** — turns that idea into an 80-word tale.
- 🔄 **Agent Handoff — Agent 1's output is stored in memory,
        then passed to Agent 2 as its input.

---

## 🎬 Live Demo

🌐 **[storyspark9.streamlit.app](https://storyspark9.streamlit.app)**

Features: Live agent panels · Dark/Light mode · Chat history · Download stories

## 🏗️ Architecture

### Pipeline Flow

| Step | Stage | Description |
|:----:|-------|-------------|
| 1️⃣ | 🎯 **Streamlit UI** | User enters Theme + Age → clicks Run Agents |
| 2️⃣ | 🎬 **Orchestrator** | `run_storyspark_streaming()` coordinates the pipeline |
| 3️⃣ | 🧠 **Agent 1 — IdeaGenerator** | Uses Wikipedia MCP tool · produces one sentence · retries once on failure |
| 4️⃣ | 💾 **Short-Term Memory** | `memory.save("idea", ...)` bridges Agent 1 to Agent 2 |
| 5️⃣ | ✍️ **Agent 2 — StoryWriter** | Reads idea from memory · writes 80-word story |
| 6️⃣ | 📝 **Final Output** | Story rendered in UI + saved to chat history |

### Component Breakdown

| Layer | Responsibility |
|-------|----------------|
| **Streamlit UI** | Captures theme + age, displays agent panels |
| **Orchestrator** | Coordinates retry logic and memory handoff |
| **Agent 1** | Uses Wikipedia to generate a story idea |
| **Short-Term Memory** | Bridges Agent 1 output to Agent 2 input |
| **Agent 2** | Consumes idea, writes children's story |
| **Output** | Rendered in UI + saved to chat history |

---

