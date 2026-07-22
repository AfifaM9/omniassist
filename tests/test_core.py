import unittest
from core.agent import OmniAssist

class TestOmniAssistCore(unittest.TestCase):
    def test_agent_initialization(self):
        agent = OmniAssist()
        self.assertIsNotNone(agent.state)
        self.assertIsNotNone(agent.tool_registry)

if __name__ == "__main__":
    unittest.main()
