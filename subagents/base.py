from abc import ABC, abstractmethod

class BaseSubAgent(ABC):
    """Abstract base class establishing the contract for all specialized sub-agents."""
    
    @abstractmethod
    def execute(self, task: str) -> str:
        """Execute the assigned specialized task."""
        pass
