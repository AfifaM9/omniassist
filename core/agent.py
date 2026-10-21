import os

import yaml
from google import genai
from google.genai import types

from core.reasoning import CognitiveEngine
from core.router import TaskRouter
from core.selfmodify import SelfModifier
from core.state import ConversationState
from mcp_tools.registry import MCPToolRegistry
from memory.vector_store import VectorStore

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

DEFAULT_MEMORY_DIR = "./data"
MAX_MEMORY_SNIPPETS = 3


class OmniAssist:
    """Main OmniAssist primary agent class coordinating lifecycle, reasoning, and tools."""
    def __init__(self):
        self.state = ConversationState()
        self.reasoning = CognitiveEngine()
        self.self_modifier = SelfModifier()
        self.tool_registry = MCPToolRegistry()
        self.router = TaskRouter(self.tool_registry)

        self.model_id = "gemini-3.6-flash-lite"
        self.fallback_models = []
        self.max_iterations = 10
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yml")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f) or {}
                    models = config_data.get("models", {}) or {}
                    self.model_id = models.get("primary", "gemini-3.6-flash-lite")
                    self.fallback_models = models.get("fallbacks", []) or []
                    agent_config = config_data.get("agent", {}) or {}
                    self.max_iterations = int(agent_config.get("max_iterations", 10) or 10)
        except Exception:
            pass

        # Long-term semantic memory lives beside the session file so a single
        # volume holds all persisted agent state.
        self.memory_dir = os.environ.get("OMNIASSIST_MEMORY_DIR", DEFAULT_MEMORY_DIR)
        self.memory = VectorStore(
            storage_path=os.path.join(self.memory_dir, "vector_index.json")
        )
        self.memory_enabled = True

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("No API key found in environment.")

        os.environ["GEMINI_API_KEY"] = api_key
        os.environ["GOOGLE_API_KEY"] = api_key
        self.client = genai.Client(api_key=api_key)

    def _build_system_prompt(self, plan: str, memories=None) -> str:
        """Generates an explicit system prompt directing multi-step autonomous behavior."""
        memory_block = ""
        if memories:
            lines = "\n".join(f"- {item['text']}" for item in memories)
            memory_block = (
                "\n### RELEVANT LONG-TERM MEMORY:\n"
                "These notes were recalled from earlier sessions and may be stale. "
                "Prefer fresh tool output whenever the two disagree.\n"
                f"{lines}\n"
            )

        return f"""You are OmniAssist, an autonomous, highly capable AI operational agent.

### CORE INSTRUCTIONS & AUTONOMY:
1. **Multi-Step Execution**: You are equipped with direct tool access. When given a complex goal, break it down into sequential, logical sub-steps. Do not ask the user for permission to execute sub-steps—take initiative using available tools.
2. **Tool Feedback Loops**: Execute tools sequentially. Inspect the results of each tool execution, evaluate if your sub-goal was achieved, adapt if errors occur, and trigger the next step until the overall task is fully resolved.
3. **Problem-Solving**: If a tool returns an error or incomplete data, retry with modified parameters or try an alternative tool before giving up.
4. **Final Response**: Once all tool calls and multi-step actions are complete, synthesize a clean, concise, and structured final summary for the user.
5. **Image & Document Input**: Use `ocr_image` (or `ocr_pdf`) to read text out of images and scanned PDFs. Never guess at the contents of a file you can read with a tool.
{memory_block}
### CURRENT CONTEXT & STRATEGIC PLAN:
{plan}
"""

    def _generate(self, contents, config) -> tuple:
        """Try each model in the priority chain until one succeeds."""
        models = [self.model_id] + [m for m in self.fallback_models if m and m != self.model_id]
        errors = []
        for model in models:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )
                return model, response
            except Exception as e:
                errors.append(f"{model}: {e}")
        raise RuntimeError("; ".join(errors))

    def _collect_tools(self) -> list:
        """Returns only true Python callables, avoiding DDGS class attribute bugs."""
        raw_tools = getattr(self.tool_registry, "tools", [])
        if isinstance(raw_tools, dict):
            raw_tools = list(raw_tools.values())
        return [t for t in raw_tools if callable(t) and not isinstance(t, type)]

    def _execute_tool_call(self, call) -> str:
        """Dispatches one model function call to the tool registry."""
        name = getattr(call, "name", None)
        if not name:
            return "Error: malformed tool call (missing name)."
        args = dict(getattr(call, "args", None) or {})
        return str(self.tool_registry.execute_tool(name, **args))

    def recall(self, query: str, top_k: int = MAX_MEMORY_SNIPPETS) -> list:
        """Returns long-term memory snippets relevant to ``query``."""
        if not self.memory_enabled:
            return []
        try:
            return self.memory.search(query, top_k=top_k)
        except Exception:
            return []

    def remember(self, doc_id: str, text: str, metadata: dict = None) -> str:
        """Stores a note in long-term semantic memory and persists the index."""
        if not self.memory_enabled:
            return "Memory disabled."
        result = self.memory.add_document(doc_id, text, metadata=metadata)
        if result.startswith("Document"):
            self.memory.save()
        return result

    def _remember_turn(self, prompt: str, response_text: str, tool_log: list) -> None:
        """Persists a compact record of the turn so future sessions can recall it."""
        if not self.memory_enabled:
            return
        try:
            # Count user turns so the first exchange is turn-0, not turn-1.
            turn_index = sum(
                1 for message in self.state.get_history() if message["role"] == "user"
            ) - 1
            tools_used = ", ".join(sorted({entry["tool"] for entry in tool_log})) or "none"
            note = (
                f"User asked: {prompt.strip()[:400]}\n"
                f"Tools used: {tools_used}\n"
                f"Answer: {str(response_text).strip()[:600]}"
            )
            self.memory.add_document(f"turn-{turn_index}", note, metadata={"tools": tools_used})
            self.memory.save()
        except Exception:
            pass

    def run(self, prompt: str) -> str:
        """Executes the agent loop, feeding tool results back until the model answers."""
        self.state.add_message("user", prompt)

        plan = self.reasoning.evaluate_plan(prompt)
        memories = self.recall(prompt)
        system_prompt = self._build_system_prompt(plan, memories)

        tool_log = []
        output_text = "Execution completed."

        try:
            config_kwargs = {
                "system_instruction": system_prompt,
                # The SDK's automatic function calling would execute tools
                # internally, bypassing the loop below. Disable it so there is
                # exactly one execution path and every call is observable.
                "automatic_function_calling": types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            }
            tools_list = self._collect_tools()
            if tools_list:
                config_kwargs["tools"] = tools_list
            config = types.GenerateContentConfig(**config_kwargs)

            contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]

            for _ in range(max(1, self.max_iterations)):
                _model_used, response = self._generate(contents, config)

                calls = getattr(response, "function_calls", None)
                if not calls:
                    output_text = getattr(response, "text", None) or "Execution completed."
                    break

                # Preserve the model's function-call turn so the API sees a
                # well-formed conversation when we hand back the results.
                if getattr(response, "candidates", None):
                    contents.append(response.candidates[0].content)

                response_parts = []
                for call in calls:
                    result = self._execute_tool_call(call)
                    tool_log.append({"tool": call.name, "args": dict(call.args or {}), "result": result})
                    response_parts.append(
                        types.Part.from_function_response(
                            name=call.name,
                            response={"result": result},
                        )
                    )
                contents.append(types.Content(role="user", parts=response_parts))
            else:
                executed = ", ".join(entry["tool"] for entry in tool_log) or "none"
                output_text = (
                    f"Stopped after {self.max_iterations} iterations without a final answer. "
                    f"Tools executed: {executed}."
                )

        except Exception as e:
            # Catch exceptions cleanly as return strings so the CLI loop never crashes and You: always stays up
            output_text = f"Agent Runtime Exception Handled: {e}"

        self.state.add_message("assistant", output_text)
        self._remember_turn(prompt, output_text, tool_log)
        self.last_tool_log = tool_log
        return output_text
