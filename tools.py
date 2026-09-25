"""Free external tools for agents."""
from crewai.tools import tool
from wikipedia_client import search_wikipedia   # ← renamed

@tool("Wikipedia Search")
def wiki_tool(topic: str) -> str:
    """Find facts about a topic using free Wikipedia API."""
    result = search_wikipedia(topic)
    return result if result else "No information found."
