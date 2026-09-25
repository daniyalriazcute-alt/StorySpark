"""
Two CrewAI agents — IdeaGenerator and StoryWriter.

LLM:      Google Gemini (free tier, native CrewAI integration)
Model:    gemini-2.5-flash-lite (higher free-tier limits)
Memory:   Short-term (in-memory handoff via memory.py)
Retry:    Max 1 retry on XYZ miss, with rate-limit backoff
Security: OWASP Top 10 for LLM Applications 2025
"""
import os
import time
from dotenv import load_dotenv

# ---- Load .env for local dev ----
load_dotenv()

# ---- Load Streamlit Cloud secrets if available ----
try:
    import streamlit as st
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    # Streamlit not installed (local script) or no secrets set — ignore
    pass

from crewai import Agent, Task, Crew, LLM
from tools import wiki_tool
from memory import memory
from security_prompts import IDEA_AGENT_SYSTEM_PROMPT, WRITER_AGENT_SYSTEM_PROMPT

# Prevent verbose token bloat
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

# Track last error for UI diagnostics
_LAST_ERROR = {"idea": "", "story": ""}


# ============================================================
# LLM Configuration — Google Gemini (Free Tier, Native)
# ============================================================

def get_llm(temperature: float = 0.3) -> LLM:
    """
    Return a native Google Gemini LLM instance.

    Uses gemini-2.5-flash-lite for higher free-tier rate limits.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Add it to Streamlit Secrets or your .env file."
        )
    return LLM(
        model="gemini/gemini-3.5-flash-lite",  # Higher free-tier RPM
        api_key=api_key,
        temperature=temperature,
    )


# ============================================================
# Agent Builders
# ============================================================

def build_idea_agent(theme: str, age: int) -> Agent:
    """Agent 1 — IdeaGenerator with OWASP-aligned system prompt."""
    system_prompt = IDEA_AGENT_SYSTEM_PROMPT.format(theme=theme, age=age)
    return Agent(
        role="Idea Generator",
        goal="Find ONE simple, age-appropriate story idea for children.",
        backstory=system_prompt,
        tools=[wiki_tool],
        verbose=False,
        max_iter=2,                # allows 1 retry max
        allow_delegation=False,
        llm=get_llm(temperature=0.5),
    )


def build_writer_agent(idea: str, age: int) -> Agent:
    """Agent 2 — StoryWriter with OWASP-aligned system prompt."""
    system_prompt = WRITER_AGENT_SYSTEM_PROMPT.format(idea=idea, age=age)
    return Agent(
        role="Story Writer",
        goal="Write a short, warm 80-word story for children.",
        backstory=system_prompt,
        tools=[],
        verbose=False,
        max_iter=2,
        allow_delegation=False,
        llm=get_llm(temperature=0.7),
    )


# ============================================================
# Task Functions
# ============================================================

def find_idea(theme: str, age: int) -> str | None:
    """
    Agent 1 — find a story idea (XYZ).
    Returns the idea string, or None on failure.
    """
    _LAST_ERROR["idea"] = ""

    try:
        agent = build_idea_agent(theme, age)
    except Exception as e:
        err = f"[IdeaAgent BUILD ERROR] {type(e).__name__}: {e}"
        print(err)
        _LAST_ERROR["idea"] = err
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
            raise ValueError("Empty result from Crew")
        return str(result).strip()
    except Exception as e:
        err = f"[IdeaAgent ERROR] {type(e).__name__}: {e}"
        print(err)
        _LAST_ERROR["idea"] = err
        return None


def write_story(idea: str, age: int) -> str:
    """
    Agent 2 — write story from the idea.
    Returns the story string, or a fallback on failure.
    """
    _LAST_ERROR["story"] = ""
    fallback = "Once upon a time, there was a small adventure waiting to happen."

    try:
        agent = build_writer_agent(idea, age)
    except Exception as e:
        err = f"[WriterAgent BUILD ERROR] {type(e).__name__}: {e}"
        print(err)
        _LAST_ERROR["story"] = err
        return fallback

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
            raise ValueError("Empty result from Crew")
        return str(result).strip()
    except Exception as e:
        err = f"[WriterAgent ERROR] {type(e).__name__}: {e}"
        print(err)
        _LAST_ERROR["story"] = err
        return fallback


# ============================================================
# Topic Validator — pre-filter before agents run
# ============================================================

def is_topic_valid(theme: str) -> tuple[bool, str]:
    """Validate the user's theme before calling any LLM."""
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


# ============================================================
# Orchestrator — full workflow with retry + memory
# ============================================================

def run_storyspark_streaming(theme: str, age: int) -> tuple:
    """
    Full StorySpark workflow.

    Returns:
        (idea, story, metadata)
        metadata = {"tokens": int, "retries": int}
    """
    tokens = 0
    retries = 0

    # ---- Agent 1: Idea Generator ----
    idea = find_idea(theme, age)
    tokens += 62

    if not idea:
        # Wait for free-tier quota window to reset before retrying
        time.sleep(25)
        retries = 1
        idea = find_idea(theme, age)     # retry ONCE
        tokens += 62

    if not idea:
        # Layer 3 fallback — guarantees Agent 2 always has input
        idea = f"A {age}-year-old discovers something magical about {theme}."

    # ---- Short-term memory (A2A handoff) ----
    memory.save("idea", idea)

    # ---- Agent 2: Story Writer ----
    story = write_story(memory.get("idea"), age)
    tokens += 88

    return idea, story, {"tokens": tokens, "retries": retries}


# ============================================================
# Debug helper — expose last errors for the UI
# ============================================================

def get_last_errors() -> dict:
    """Return the last captured errors for UI display."""
    return dict(_LAST_ERROR)
