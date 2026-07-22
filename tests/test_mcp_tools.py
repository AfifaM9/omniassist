import unittest
from mcp_tools.registry import MCPToolRegistry

class TestMCPTools(unittest.TestCase):
    def test_registry_loading(self):
        registry = MCPToolRegistry()
        self.assertGreater(len(registry.tools), 0)

if __name__ == "__main__":
    unittest.main()
