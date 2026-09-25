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
- 🔄 **A2A Handoff** — they talk to each other through short-term memory.

---

## 🎬 Live Demo

🌐 **[storyspark9.streamlit.app](https://storyspark9.streamlit.app)**

Features: Live agent panels · Dark/Light mode · Chat history · Download stories

---

## 🏗️ Architecture

**Pipeline Flow:**
🎯 Streamlit UI (Theme + Age input)
│
▼
🎬 Orchestrator — run_storyspark_streaming()
│
├──► 🧠 Agent 1 — IdeaGenerator
│ • Wikipedia MCP tool
│ • Produces one sentence
│ • Retry once on failure
│ │
│ ▼
│ 💾 Short-Term Memory
│ │
│ ▼
└──► ✍️ Agent 2 — StoryWriter
• Reads idea from memory
• Writes 80-word story
│
▼
📝 Final Story → Chat History → Streamlit Display
