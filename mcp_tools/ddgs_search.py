from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 3) -> str:
    """Performs a web search using DuckDuckGo and returns synthesized text results."""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get("title", "No Title")
                href = r.get("href", "#")
                body = r.get("body", "No description available.")
                results.append(f"**{title}**\n{href}\n{body}\n")
        
        if not results:
            return "No relevant search results found."
        return "\n".join(results)
    except Exception as e:
        return f"Search Execution Error: {e}"
