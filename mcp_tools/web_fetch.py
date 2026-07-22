import urllib.request

def web_fetch(url: str) -> str:
    """Fetches the contents of a webpage in clean markdown format using Jina Reader (https://r.jina.ai/) without requiring an API key."""
    try:
        target_url = url.strip()
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url
            
        jina_url = f"https://r.jina.ai/{target_url}"
        req = urllib.request.Request(
            jina_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode("utf-8", errors="ignore")
            if not content.strip():
                return f"Warning: Received empty content from Jina Reader for URL: {target_url}"
            return content
    except Exception as e:
        return f"Web Fetch Error: {e}"
