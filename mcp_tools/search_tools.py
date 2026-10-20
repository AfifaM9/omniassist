import json
import urllib.request


def api_lookup(endpoint: str) -> str:
    """Performs a simple GET request to a public API endpoint."""
    try:
        req = urllib.request.Request(
            endpoint,
            headers={"User-Agent": "OmniAssist-Agent/2026.6 \"Dirt Cake\""}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode("utf-8")
            parsed = json.loads(data)
            return json.dumps(parsed, indent=2)
    except Exception as e:
        return f"API Lookup Error: {e}"
