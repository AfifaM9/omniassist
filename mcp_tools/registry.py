import importlib
import pkgutil
import mcp_tools

class MCPToolRegistry:
    """Dynamically discovers and executes registered Model Context Protocol (MCP) tools."""
    def __init__(self):
        self.tools = {}
        self._discover_tools()

    def _discover_tools(self):
        """Auto-loads modules inside the mcp_tools package."""
        for _, modname, _ in pkgutil.iter_modules(mcp_tools.__path__):
            if modname != "registry":
                module = importlib.import_module(f"mcp_tools.{modname}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and not attr_name.startswith("_"):
                        self.tools[attr_name] = attr

    def execute_tool(self, tool_name: str, *args, **kwargs):
        """Executes a registered tool function by name."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found in registry."
        try:
            return self.tools[tool_name](*args, **kwargs)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {e}"
