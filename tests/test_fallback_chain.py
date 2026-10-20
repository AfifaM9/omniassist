import unittest

from core.agent import OmniAssist


class _FakeResponse:
    text = "ok"


class _FakeModels:
    def __init__(self, fake_client):
        self._fake_client = fake_client

    def generate_content(self, model, contents, config):
        self._fake_client.calls.append(model)
        if model in self._fake_client.succeed_on:
            return _FakeResponse()
        raise RuntimeError(f"model {model} unavailable")


class _FakeClient:
    def __init__(self, succeed_on=None):
        self.succeed_on = succeed_on or []
        self.calls = []
        self.models = _FakeModels(self)


class TestFallbackChain(unittest.TestCase):
    def _make_agent(self, model_id, fallbacks, succeed_on):
        agent = object.__new__(OmniAssist)
        agent.model_id = model_id
        agent.fallback_models = fallbacks
        agent.client = _FakeClient(succeed_on=succeed_on)
        return agent

    def test_primary_model_used_first(self):
        agent = self._make_agent(
            "gemini-3.5-flash-lite",
            ["gemini-3.1-flash-lite", "gemini-3-flash"],
            succeed_on=["gemini-3.5-flash-lite"],
        )
        model_used, _ = agent._generate("hello", config=None)
        self.assertEqual(model_used, "gemini-3.5-flash-lite")
        self.assertEqual(agent.client.calls, ["gemini-3.5-flash-lite"])

    def test_falls_back_to_next_model_on_failure(self):
        agent = self._make_agent(
            "gemini-3.5-flash-lite",
            ["gemini-3.1-flash-lite", "gemini-3-flash"],
            succeed_on=["gemini-3.1-flash-lite"],
        )
        model_used, _ = agent._generate("hello", config=None)
        self.assertEqual(model_used, "gemini-3.1-flash-lite")
        self.assertEqual(
            agent.client.calls,
            ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"],
        )

    def test_primary_then_all_fallbacks(self):
        agent = self._make_agent(
            "gemini-3.5-flash-lite",
            ["gemini-3.1-flash-lite", "gemini-3-flash"],
            succeed_on=["gemini-3-flash"],
        )
        model_used, _ = agent._generate("hello", config=None)
        self.assertEqual(model_used, "gemini-3-flash")
        self.assertEqual(
            agent.client.calls,
            ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3-flash"],
        )

    def test_raises_when_all_models_fail(self):
        agent = self._make_agent(
            "gemini-3.5-flash-lite",
            ["gemini-3.1-flash-lite", "gemini-3-flash"],
            succeed_on=[],
        )
        with self.assertRaises(RuntimeError):
            agent._generate("hello", config=None)
        self.assertEqual(
            agent.client.calls,
            ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3-flash"],
        )

    def test_duplicate_fallbacks_skipped(self):
        agent = self._make_agent(
            "gemini-3.5-flash-lite",
            ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"],
            succeed_on=["gemini-3.1-flash-lite"],
        )
        model_used, _ = agent._generate("hello", config=None)
        self.assertEqual(model_used, "gemini-3.1-flash-lite")
        self.assertEqual(agent.client.calls, ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"])


if __name__ == "__main__":
    unittest.main()
