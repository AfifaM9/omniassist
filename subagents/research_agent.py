from subagents.base import BaseSubAgent

class ResearchAgent(BaseSubAgent):
    """Specialized sub-agent for information retrieval and document synthesis."""
    def execute(self, task: str) -> str:
        return f"[ResearchAgent] Synthesizing findings for: {task}"
