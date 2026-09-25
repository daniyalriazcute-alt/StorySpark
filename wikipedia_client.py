"""Wikipedia API client — free knowledge source for agents."""
import wikipediaapi


# ---------- Wikipedia API Setup ----------
wiki = wikipediaapi.Wikipedia(
    user_agent="StorySpark/1.0 (educational)",
    language="en",
)


# ---------- Public Function ----------
def search_wikipedia(topic: str, max_chars: int = 200) -> str | None:
    """
    Return a short Wikipedia summary for a topic, or None if not found.

    Args:
        topic: The search term (e.g. "friendship").
        max_chars: Maximum characters to return (default 200).
                   Kept short to stay within token budget.

    Returns:
        A short summary string, or None if the page doesn't exist
        or an error occurs.
    """
    try:
        page = wiki.page(topic)
        if page.exists():
            return page.summary[:max_chars]
    except Exception as e:
        print(f"[Wikipedia ERROR] {type(e).__name__}: {e}")
    return None
