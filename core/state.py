class ConversationState:
    """Tracks active conversation history and runtime execution context."""
    def __init__(self):
        self.history = []

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_history(self):
        return self.history
