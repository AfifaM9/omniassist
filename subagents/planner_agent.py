from subagents.base import BaseSubAgent

class PlannerAgent(BaseSubAgent):
    """Specialized sub-agent for complex task breakdown and multi-step planning."""
    def execute(self, task: str) -> str:
        return f"[PlannerAgent] Deconstructing complex workflow for: {task}"
