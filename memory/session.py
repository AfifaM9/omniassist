import json
import os

class SessionPersistence:
    """Session state saving and loading across agent reboots."""
    def __init__(self, session_file: str = "./data/session_state.json"):
        self.session_file = session_file

    def save_session(self, state_data: dict):
        """Saves current session context to disk."""
        try:
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=4)
            return "Session saved successfully."
        except Exception as e:
            return f"Session Save Error: {e}"

    def load_session(self) -> dict:
        """Loads previous session context from disk."""
        if not os.path.exists(self.session_file):
            return {}
        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
