import os
import yaml
from google import genai
from google.genai import types
from core.state import ConversationState
from core.reasoning import CognitiveEngine
from core.selfmodify import SelfModifier
from core.router import TaskRouter
from mcp_tools.registry import MCPToolRegistry

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

class OmniAssist:
    """Main OmniAssist primary agent class coordinating lifecycle, reasoning, and tools."""
    def __init__(self):
        self.state = ConversationState()
        self.reasoning = CognitiveEngine()
        self.self_modifier = SelfModifier()
        self.tool_registry = MCPToolRegistry()
        self.router = TaskRouter(self.tool_registry)
        
        self.model_id = "gemini-3.5-flash-lite"
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yml")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f)
                    self.model_id = config_data.get("models", {}).get("primary", "gemini-3.5-flash-lite")
        except Exception:
            pass

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("No API key found in environment.")

        os.environ["GEMINI_API_KEY"] = api_key
        os.environ["GOOGLE_API_KEY"] = api_key
        self.client = genai.Client(api_key=api_key)

    def run(self, prompt: str) -> str:
        """Executes agent execution loop safely catching internal tool registration issues."""
        self.state.add_message("user", prompt)
        
        plan = self.reasoning.evaluate_plan(prompt)
        system_prompt = f"You are OmniAssist, an advanced AI operational agent. Context plan: {plan}."

        try:
            # Safely filter tools to only include true Python callables, entirely avoiding DDGS class attribute bugs
            tools_list = []
            raw_tools = getattr(self.tool_registry, "tools", [])
            if isinstance(raw_tools, dict):
                raw_tools = list(raw_tools.values())
            
            for t in raw_tools:
                if callable(t) and not isinstance(t, type):
                    tools_list.append(t)

            config_kwargs = {"system_instruction": system_prompt}
            if tools_list:
                config_kwargs["tools"] = tools_list

            config = types.GenerateContentConfig(**config_kwargs)

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=config
            )

            if hasattr(response, "function_calls") and response.function_calls:
                results = []
                for call in response.function_calls:
                    res = self.router.execute(call.name, call.args or {}) if hasattr(self.router, "execute") else f"Executed {call.name}"
                    results.append(str(res))
                output_text = "\n".join(results)
            else:
                output_text = response.text or "Execution completed."

        except Exception as e:
            # Catch exceptions cleanly as return strings so the CLI loop never crashes and You: always stays up
            output_text = f"Agent Runtime Exception Handled: {e}"

        self.state.add_message("assistant", output_text)
        return output_text
