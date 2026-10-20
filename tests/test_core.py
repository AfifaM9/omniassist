import os
import unittest
from unittest.mock import patch

from core.agent import OmniAssist


class TestOmniAssistCore(unittest.TestCase):
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=False)
    def test_agent_initialization(self):
        agent = OmniAssist()
        self.assertIsNotNone(agent.state)
        self.assertIsNotNone(agent.tool_registry)

if __name__ == "__main__":
    unittest.main()
