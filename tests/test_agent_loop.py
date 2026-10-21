"""Tests for the agent execution loop.

These cover the tool-call path directly. Before v2026.7 the loop dispatched to
``TaskRouter.execute``, which does not exist, so every tool call silently
returned the string "Executed <tool>" and no tool ever ran. These tests fail
against that behaviour.
"""

import os
import unittest
from tempfile import TemporaryDirectory

from google.genai import types

from core.agent import OmniAssist
from core.reasoning import CognitiveEngine
from core.router import TaskRouter
from core.state import ConversationState
from mcp_tools.registry import MCPToolRegistry
from memory.vector_store import HashingEmbedder, VectorStore


class FakeCall:
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or {}


class FakeResponse:
    """Minimal stand-in for a google-genai GenerateContentResponse."""

    def __init__(self, text=None, calls=None):
        self.text = text
        self.function_calls = calls or []
        self.candidates = []
        if self.function_calls:
            # Mirrors the real SDK shape: candidates[i].content is a Content.
            self.candidates = [
                types.Candidate(
                    content=types.Content(role="model", parts=[types.Part(text=text or "")])
                )
            ]


class FakeClient:
    """Returns queued responses in order and records the contents it received."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.received = []

    def models(self):
        raise NotImplementedError


def make_agent(responses, tmpdir=None):
    """Builds an OmniAssist without touching the network or the API key."""
    agent = object.__new__(OmniAssist)
    agent.state = ConversationState()
    agent.reasoning = CognitiveEngine()
    agent.tool_registry = MCPToolRegistry()
    agent.router = TaskRouter(agent.tool_registry)
    agent.model_id = "test-model"
    agent.fallback_models = []
    agent.max_iterations = 5
    agent.memory_enabled = True
    agent.memory_dir = tmpdir or "/tmp"
    agent.memory = VectorStore(
        storage_path=os.path.join(agent.memory_dir, "vector_index.json"),
        embedder=HashingEmbedder(),
    )
    agent.last_tool_log = []

    queue = list(responses)

    def fake_generate(contents, config):
        agent.last_config = config
        agent.last_contents = contents
        if not queue:
            raise AssertionError("agent called the model more times than expected")
        return "test-model", queue.pop(0)

    agent._generate = fake_generate
    return agent


class TestToolExecution(unittest.TestCase):
    """The core regression: function calls must actually run the tool."""

    def test_tool_call_executes_registered_tool(self):
        agent = make_agent([
            FakeResponse(calls=[FakeCall("basic_calculate", {"expression": "6*7"})]),
            FakeResponse(text="The answer is 42."),
        ])
        result = agent.run("what is 6*7?")
        self.assertEqual(result, "The answer is 42.")
        self.assertEqual(len(agent.last_tool_log), 1)
        self.assertEqual(agent.last_tool_log[0]["tool"], "basic_calculate")
        self.assertEqual(agent.last_tool_log[0]["result"], "42")

    def test_tool_result_is_fed_back_to_the_model(self):
        agent = make_agent([
            FakeResponse(calls=[FakeCall("basic_calculate", {"expression": "2+2"})]),
            FakeResponse(text="done"),
        ])
        agent.run("add")
        # contents: [user prompt, model function-call turn, function responses]
        self.assertEqual(len(agent.last_contents), 3)
        response_parts = agent.last_contents[-1].parts
        self.assertEqual(len(response_parts), 1)
        self.assertIn("function_response", str(response_parts[0]).lower())

    def test_no_tool_call_returns_text_immediately(self):
        agent = make_agent([FakeResponse(text="Plain answer.")])
        self.assertEqual(agent.run("hi"), "Plain answer.")
        self.assertEqual(agent.last_tool_log, [])

    def test_multiple_tool_calls_in_one_turn(self):
        agent = make_agent([
            FakeResponse(calls=[
                FakeCall("basic_calculate", {"expression": "1+1"}),
                FakeCall("basic_calculate", {"expression": "3+3"}),
            ]),
            FakeResponse(text="both done"),
        ])
        agent.run("two sums")
        self.assertEqual([e["result"] for e in agent.last_tool_log], ["2", "6"])

    def test_unknown_tool_returns_error_without_crashing(self):
        agent = make_agent([
            FakeResponse(calls=[FakeCall("no_such_tool", {})]),
            FakeResponse(text="recovered"),
        ])
        agent.run("call a missing tool")
        self.assertIn("not found", agent.last_tool_log[0]["result"])

    def test_tool_exception_is_reported_not_raised(self):
        def boom(**kwargs):
            raise ValueError("tool exploded")

        agent = make_agent([
            FakeResponse(calls=[FakeCall("boom_tool", {})]),
            FakeResponse(text="recovered"),
        ])
        agent.tool_registry.tools["boom_tool"] = boom
        agent.run("trigger failure")
        self.assertIn("tool exploded", agent.last_tool_log[0]["result"])

    def test_malformed_call_without_name(self):
        agent = make_agent([
            FakeResponse(calls=[FakeCall(None)]),
            FakeResponse(text="recovered"),
        ])
        agent.run("bad call")
        self.assertIn("malformed", agent.last_tool_log[0]["result"])

    def test_none_args_are_tolerated(self):
        class NoArgsCall:
            name = "basic_calculate"
            args = None

        agent = make_agent([
            FakeResponse(calls=[NoArgsCall()]),
            FakeResponse(text="ok"),
        ])
        agent.run("no args")
        # Missing required argument surfaces as a tool error, not a crash.
        self.assertIn("Error", agent.last_tool_log[0]["result"])

    def test_real_ocr_tool_is_reachable_through_the_loop(self):
        """End-to-end: a function call to ocr_image reaches the real tool."""
        agent = make_agent([
            FakeResponse(calls=[FakeCall("ocr_image", {"file_path": "/definitely/missing.png"})]),
            FakeResponse(text="handled"),
        ])
        agent.run("read that image")
        self.assertIn("file not found", agent.last_tool_log[0]["result"])


class TestLoopControl(unittest.TestCase):
    def test_iteration_cap_stops_runaway_loops(self):
        endless = [
            FakeResponse(calls=[FakeCall("basic_calculate", {"expression": "1+1"})])
            for _ in range(5)
        ]
        agent = make_agent(endless)
        agent.max_iterations = 3
        result = agent.run("loop forever")
        self.assertIn("Stopped after 3 iterations", result)
        self.assertEqual(len(agent.last_tool_log), 3)

    def test_model_exception_is_handled(self):
        agent = make_agent([])

        def raising(contents, config):
            raise RuntimeError("model chain exhausted")

        agent._generate = raising
        result = agent.run("anything")
        self.assertIn("Agent Runtime Exception Handled", result)
        self.assertIn("model chain exhausted", result)

    def test_history_records_both_turns(self):
        agent = make_agent([FakeResponse(text="reply")])
        agent.run("question")
        history = agent.state.get_history()
        self.assertEqual([m["role"] for m in history], ["user", "assistant"])
        self.assertEqual(history[1]["content"], "reply")

    def test_empty_text_falls_back_to_default(self):
        agent = make_agent([FakeResponse(text=None)])
        self.assertEqual(agent.run("hi"), "Execution completed.")

    def test_config_receives_tool_declarations(self):
        agent = make_agent([FakeResponse(text="ok")])
        agent.run("hi")
        self.assertTrue(getattr(agent.last_config, "tools", None))

    def test_automatic_function_calling_is_disabled(self):
        """The SDK must not execute tools behind the loop's back.

        Automatic function calling is on by default in google-genai. Left
        enabled, tools run inside the SDK and never appear in last_tool_log,
        making execution invisible (and memory records say "Tools used: none").
        """
        agent = make_agent([FakeResponse(text="ok")])
        agent.run("hi")
        afc = getattr(agent.last_config, "automatic_function_calling", None)
        self.assertIsNotNone(afc, "automatic_function_calling was not configured")
        self.assertTrue(afc.disable, "automatic function calling must be disabled")


class TestMemoryIntegration(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.tmp = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_turn_is_written_to_long_term_memory(self):
        agent = make_agent([FakeResponse(text="the answer is 42")], tmpdir=self.tmp)
        agent.run("what is the answer?")
        self.assertEqual(len(agent.memory), 1)
        self.assertIn("what is the answer?", agent.memory.get_document("turn-0")["text"])

    def test_index_is_persisted_to_disk(self):
        agent = make_agent([FakeResponse(text="saved")], tmpdir=self.tmp)
        agent.run("persist this")
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "vector_index.json")))

    def test_prior_memory_is_recalled_into_the_system_prompt(self):
        agent = make_agent([FakeResponse(text="ok")], tmpdir=self.tmp)
        agent.remember("note-1", "the deployment password rotates every friday")
        recalled = agent.recall("when does the deployment password rotate?", top_k=1)
        self.assertEqual(recalled[0]["doc_id"], "note-1")

        agent.run("when does the deployment password rotate?")
        instruction = agent.last_config.system_instruction
        self.assertIn("RELEVANT LONG-TERM MEMORY", instruction)
        self.assertIn("rotates every friday", instruction)

    def test_no_memory_block_when_nothing_matches(self):
        agent = make_agent([FakeResponse(text="ok")], tmpdir=self.tmp)
        agent.run("first ever question")
        # turn-0 is written after the prompt, so the prompt sees an empty store.
        self.assertNotIn("RELEVANT LONG-TERM MEMORY", agent.last_config.system_instruction)

    def test_remember_persists_across_agent_instances(self):
        first = make_agent([FakeResponse(text="a")], tmpdir=self.tmp)
        first.remember("fact-1", "tesseract is the OCR engine")

        second = make_agent([FakeResponse(text="b")], tmpdir=self.tmp)
        self.assertEqual(len(second.memory), 1)
        self.assertIn("tesseract", second.memory.get_document("fact-1")["text"])

    def test_memory_disabled_skips_reads_and_writes(self):
        agent = make_agent([FakeResponse(text="ok")], tmpdir=self.tmp)
        agent.memory_enabled = False
        agent.run("nothing should be stored")
        self.assertEqual(len(agent.memory), 0)
        self.assertEqual(agent.recall("anything"), [])

    def test_tool_usage_recorded_in_memory_note(self):
        agent = make_agent([
            FakeResponse(calls=[FakeCall("basic_calculate", {"expression": "5*5"})]),
            FakeResponse(text="25"),
        ], tmpdir=self.tmp)
        agent.run("multiply")
        note = agent.memory.get_document("turn-0")["text"]
        self.assertIn("basic_calculate", note)


if __name__ == "__main__":
    unittest.main()
