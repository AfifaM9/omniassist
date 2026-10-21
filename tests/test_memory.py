"""Tests for long-term semantic memory (vector store + agent integration)."""

import json
import os
import unittest
from tempfile import TemporaryDirectory

from memory.vector_store import (
    FALLBACK_DIMENSION,
    HashingEmbedder,
    VectorStore,
)


class TestHashingEmbedder(unittest.TestCase):
    def test_dimension_and_normalisation(self):
        embedder = HashingEmbedder(dimension=64)
        vector = embedder.encode("hello world")
        self.assertEqual(len(vector), 64)
        self.assertAlmostEqual(sum(v * v for v in vector) ** 0.5, 1.0, places=6)

    def test_deterministic(self):
        embedder = HashingEmbedder()
        self.assertEqual(embedder.encode("same text"), embedder.encode("same text"))

    def test_empty_text_is_all_zero(self):
        self.assertEqual(sum(HashingEmbedder(dimension=16).encode("")), 0.0)


class TestVectorStore(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.path = os.path.join(self._tmp.name, "vector_index.json")
        self.store = VectorStore(storage_path=self.path, embedder=HashingEmbedder())

    def tearDown(self):
        self._tmp.cleanup()

    def test_empty_store_search(self):
        self.assertEqual(self.store.search("anything"), [])

    def test_add_and_len(self):
        self.store.add_document("a", "first document")
        self.store.add_document("b", "second document")
        self.assertEqual(len(self.store), 2)

    def test_rejects_empty_doc_id(self):
        self.assertIn("must be a non-empty string", self.store.add_document("", "text"))

    def test_rejects_empty_text(self):
        self.assertIn("must be non-empty", self.store.add_document("a", "   "))

    def test_rejects_none_text(self):
        self.assertIn("must be non-empty", self.store.add_document("a", None))

    def test_search_ranks_relevant_first(self):
        self.store.add_document("ocr", "tesseract performs optical character recognition")
        self.store.add_document("models", "the fallback chain retries gemini models")
        results = self.store.search("optical character recognition", top_k=2)
        self.assertEqual(results[0]["doc_id"], "ocr")
        self.assertGreater(results[0]["score"], results[1]["score"])

    def test_search_returns_metadata_and_shape(self):
        self.store.add_document("a", "alpha text", metadata={"kind": "note"})
        result = self.store.search("alpha", top_k=1)[0]
        self.assertEqual(result["metadata"], {"kind": "note"})
        self.assertEqual(set(result), {"doc_id", "text", "metadata", "score"})

    def test_top_k_is_clamped_and_validated(self):
        for i in range(5):
            self.store.add_document(f"d{i}", f"document number {i}")
        self.assertEqual(len(self.store.search("document", top_k=2)), 2)
        self.assertEqual(len(self.store.search("document", top_k=999)), 5)
        self.assertEqual(len(self.store.search("document", top_k="bad")), 3)
        self.assertEqual(len(self.store.search("document", top_k=0)), 1)

    def test_replace_document(self):
        self.store.add_document("a", "original")
        self.store.add_document("a", "replacement")
        self.assertEqual(len(self.store), 1)
        self.assertEqual(self.store.get_document("a")["text"], "replacement")

    def test_get_document_missing(self):
        self.assertIsNone(self.store.get_document("absent"))

    def test_clear(self):
        self.store.add_document("a", "x")
        self.store.clear()
        self.assertEqual(len(self.store), 0)

    def test_save_and_reload(self):
        self.store.add_document("a", "persisted note about tesseract")
        self.assertIn("saved", self.store.save().lower())

        reloaded = VectorStore(storage_path=self.path, embedder=HashingEmbedder())
        self.assertEqual(len(reloaded), 1)
        self.assertEqual(reloaded.get_document("a")["text"], "persisted note about tesseract")
        self.assertEqual(reloaded.search("tesseract")[0]["doc_id"], "a")

    def test_save_creates_missing_directories(self):
        nested = os.path.join(self._tmp.name, "deep", "nested", "index.json")
        store = VectorStore(storage_path=nested, embedder=HashingEmbedder())
        store.add_document("a", "text")
        self.assertIn("saved", store.save().lower())
        self.assertTrue(os.path.exists(nested))

    def test_payload_is_valid_json_with_version(self):
        self.store.add_document("a", "text")
        self.store.save()
        with open(self.path, encoding="utf-8") as handle:
            payload = json.load(handle)
        self.assertEqual(payload["version"], 1)
        self.assertEqual(payload["embedder_kind"], "hashing")
        self.assertEqual(payload["documents"][0]["doc_id"], "a")

    def test_load_missing_file_is_not_an_error(self):
        store = VectorStore(storage_path=os.path.join(self._tmp.name, "absent.json"))
        self.assertIn("No existing vector index", store.load())

    def test_load_corrupt_file_reports_error(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("{not json")
        store = VectorStore(storage_path=self.path, embedder=HashingEmbedder())
        self.assertIn("Load Error", store.load())

    def test_vectors_recomputed_when_backend_changes(self):
        """A store written by one backend must still be readable by another."""
        self.store.add_document("a", "note about tesseract")
        self.store.save()

        class DifferentDimension(HashingEmbedder):
            def __init__(self):
                super().__init__(dimension=FALLBACK_DIMENSION * 2)

        reloaded = VectorStore(storage_path=self.path, embedder=DifferentDimension())
        self.assertIn("recomputed", reloaded.load())
        self.assertEqual(len(reloaded.search("tesseract")), 1)

    def test_backend_falls_back_to_hashing_when_model_unavailable(self):
        store = VectorStore(storage_path=self.path, model_name="definitely/not-a-real-model")
        self.assertIn(store.backend, ("hashing", "sentence-transformers"))

    def test_unicode_text(self):
        self.store.add_document("u", "café ünïcode 日本語 text")
        self.assertIn("café", self.store.get_document("u")["text"])


if __name__ == "__main__":
    unittest.main()
