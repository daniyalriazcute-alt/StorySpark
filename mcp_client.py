"""Free MCP connector — Wikipedia."""
import wikipediaapi


wiki = wikipediaapi.Wikipedia(
    user_agent="StorySpark/1.0 (educational)",
    language="en",
)


def search_wikipedia(topic: str, max_chars: int = 200) -> str | None:
    """Return a short Wikipedia summary or None if not found."""
    try:
        page = wiki.page(topic)
        if page.exists():
            return page.summary[:max_chars]
    except Exception:
        pass
    return None
