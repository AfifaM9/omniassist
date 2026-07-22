class ConversationMemory:
    """Short-term conversational message buffer."""
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history = []

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_context(self) -> list:
        return self.history
