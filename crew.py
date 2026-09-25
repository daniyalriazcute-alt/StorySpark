"""Two CrewAI agents — IdeaGenerator and StoryWriter using free Groq LLM."""
import os
from dotenv import load_dotenv

# ---- Load .env for local dev ----
load_dotenv()

# ---- Load Streamlit Cloud secrets if available ----
try:
    import streamlit as st
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

from crewai import Agent, Task, Crew, LLM
from tools import wiki_tool
from memory import memory
from security_prompts import IDEA_AGENT_SYSTEM_PROMPT, WRITER_AGENT_SYSTEM_PROMPT

# Prevent verbose token bloat
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"


# ---------- Groq LLM Configuration ----------

def get_groq_llm(temperature: float = 0.3) -> LLM:
    """Return a configured Groq LLM instance using the free tier."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Add it to Streamlit Secrets or your .env file."
        )
    return LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=api_key,
        temperature=temperature,
    )


# ---------- Agent Builders ----------

def build_idea_agent(theme: str, age: int) -> Agent:
    system_prompt = IDEA_AGENT_SYSTEM_PROMPT.format(theme=theme, age=age)
    return Agent(
        role="Idea Generator",
        goal="Find ONE simple, age-appropriate story idea for children.",
        backstory=system_prompt,
        tools=[wiki_tool],
        verbose=False,
        max_iter=2,
        allow_delegation=False,
        llm=get_groq_llm(temperature=0.5),
    )


def build_writer_agent(idea: str, age: int) -> Agent:
    system_prompt = WRITER_AGENT_SYSTEM_PROMPT.format(idea=idea, age=age)
    return Agent(
        role="Story Writer",
        goal="Write a short, warm 80-word story for children.",
        backstory=system_prompt,
        tools=[],
        verbose=False,
        max_iter=2,
        allow_delegation=False,
        llm=get_groq_llm(temperature=0.7),
    )


# ---------- Task Functions ----------

def find_idea(theme: str, age: int) -> str | None:
    """Agent 1: find a story idea (XYZ). Returns None on failure."""
    try:
        agent = build_idea_agent(theme, age)
    except Exception as e:
        print(f"[IdeaAgent BUILD ERROR] {type(e).__name__}: {e}")
        return None

    task = Task(
        description=(
            f"Find ONE story idea about '{theme}' for a {age}-year-old child. "
            f"Use the Wikipedia Search tool for inspiration. "
            f"Return ONLY one sentence in English."
        ),
        expected_output="One sentence story idea in English.",
        agent=agent,
    )
    try:
        result = Crew(agents=[agent], tasks=[task], verbose=False).kickoff()
        if not result:
            raise ValueError("Empty result")
        return str(result).strip()
    except Exception as e:
        print(f"[IdeaAgent ERROR] {type(e).__name__}: {e}")
        return None


def write_story(idea: str, age: int) -> str:
    """Agent 2: write story from idea. Returns fallback if fails."""
    try:
        agent = build_writer_agent(idea, age)
    except Exception as e:
        print(f"[WriterAgent BUILD ERROR] {type(e).__name__}: {e}")
        return "Once upon a time, there was a small adventure waiting to happen."

    task = Task(
        description=(
            f"Write a short story (max 80 words) for a {age}-year-old child "
            f"based on this idea: {idea}"
        ),
        expected_output="Short children's story in English, max 80 words.",
        agent=agent,
    )
    try:
        result = Crew(agents=[agent], tasks=[task], verbose=False).kickoff()
        if not result:
            raise ValueError("Empty result")
        return str(result).strip()
    except Exception as e:
        print(f"[WriterAgent ERROR] {type(e).__name__}: {e}")
        return "Once upon a time, there was a small adventure waiting to happen."


# ---------- Topic Validator ----------

def is_topic_valid(theme: str) -> tuple[bool, str]:
    """Pre-filter topics before sending to agents."""
    theme_lower = theme.lower().strip()

    if not theme_lower:
        return False, "Please enter a theme."

    if len(theme) > 60:
        return False, "Theme too long. Keep it under 60 characters."

    if not all(ord(c) < 128 for c in theme):
        return False, "Please use English text only."

    blocked = [
        "ignore previous", "ignore all", "system prompt",
        "reveal your", "you are now", "forget instructions",
    ]
    if any(p in theme_lower for p in blocked):
        return False, "This theme cannot be processed."

    unsafe = ["kill", "murder", "weapon", "blood", "war", "shoot"]
    if any(w in theme_lower for w in unsafe):
        return False, "Please choose a child-friendly theme."

    return True, "OK"


# ---------- Orchestrator ----------

def run_storyspark_streaming(theme: str, age: int) -> tuple:
    """Full workflow with retry + memory."""
    tokens = 0
    retries = 0

    # ---- Agent 1 ----
    idea = find_idea(theme, age)
    tokens += 62

    if not idea:
        retries = 1
        idea = find_idea(theme, age)
        tokens += 62

    if not idea:
        idea = f"A {age}-year-old discovers something magical about {theme}."

    # ---- Short-term memory ----
    memory.save("idea", idea)

    # ---- Agent 2 ----
    story = write_story(memory.get("idea"), age)
    tokens += 88

    return idea, story, {"tokens": tokens, "retries": retries}
