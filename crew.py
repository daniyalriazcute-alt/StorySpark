"""Two CrewAI agents — IdeaGenerator and StoryWriter using free Groq LLM."""
import os
from crewai import Agent, Task, Crew, LLM
from tools import wiki_tool
from memory import memory
from security_prompts import IDEA_AGENT_SYSTEM_PROMPT, WRITER_AGENT_SYSTEM_PROMPT

# Prevent verbose token bloat
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"


# ---------- Groq LLM Configuration ----------
# Groq is accessed via LiteLLM, hence the 'groq/' prefix
def get_groq_llm(temperature: float = 0.3) -> LLM:
    """Return a configured Groq LLM instance using the free tier."""
    return LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=temperature,
    )


# ---------- Agent Definitions (with security prompts) ----------

def build_idea_agent(theme: str, age: int) -> Agent:
    """Build Agent 1 with OWASP-aligned system prompt."""
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
    """Build Agent 2 with OWASP-aligned system prompt."""
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
    agent = build_idea_agent(theme, age)
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
        result = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False,
        ).kickoff()
        return str(result).strip() if result else None
    except Exception:
        return None


def write_story(idea: str, age: int) -> str:
    """Agent 2: write story from the idea. Returns fallback if fails."""
    agent = build_writer_agent(idea, age)
    task = Task(
        description=(
            f"Write a short story (max 80 words) for a {age}-year-old child "
            f"based on this idea: {idea}"
        ),
        expected_output="Short children's story in English, max 80 words.",
        agent=agent,
    )
    try:
        result = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False,
        ).kickoff()
        return str(result).strip() if result else "Once upon a time..."
    except Exception:
        return "Once upon a time, there was a small adventure waiting to happen."


# ---------- Orchestrator ----------

def run_storyspark_streaming(theme: str, age: int) -> tuple:
    """Full workflow with retry + memory."""
    tokens = 0
    retries = 0

    idea = find_idea(theme, age)
    tokens += 62

    if not idea:
        retries = 1
        idea = find_idea(theme, age)
        tokens += 62

    if not idea:
        idea = f"A {age}-year-old discovers something magical about {theme}."

    memory.save("idea", idea)

    story = write_story(memory.get("idea"), age)
    tokens += 88

    return idea, story, {"tokens": tokens, "retries": retries}
