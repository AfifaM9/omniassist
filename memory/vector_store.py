"""Long-term semantic memory: a small, dependency-light vector index.

Embeddings come from ``sentence-transformers`` when it is installed. When it is
not, a deterministic hashing embedder keeps semantic search functional so the
agent never hard-fails on a missing optional dependency. Vectors are persisted
alongside the raw text, so a store written by one backend can still be read by
another (the vectors are simply recomputed).
"""

import json
import math
import os
import re
import zlib

FALLBACK_DIMENSION = 512
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
STORAGE_VERSION = 1
_TOKEN_PATTERN = re.compile(r"[a-z0-9']+")


def _tokenize(text: str):
    return _TOKEN_PATTERN.findall(str(text).lower())


def _normalise(vector):
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return list(vector)
    return [value / norm for value in vector]


class HashingEmbedder:
    """Deterministic bag-of-words embedder used when no model is available."""

    kind = "hashing"

    def __init__(self, dimension: int = FALLBACK_DIMENSION):
        self.dimension = dimension

    def encode(self, text: str):
        vector = [0.0] * self.dimension
        for token in _tokenize(text):
            index = zlib.crc32(token.encode("utf-8")) % self.dimension
            vector[index] += 1.0
        return _normalise(vector)


class SentenceTransformerEmbedder:
    """Semantic embedder wrapping a lazily-loaded sentence-transformers model."""

    kind = "sentence-transformers"

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        self.dimension = len(self.encode("dimension probe"))

    def encode(self, text: str):
        vector = self._model.encode([str(text)], convert_to_numpy=True)[0]
        return _normalise([float(value) for value in vector])


def _cosine(left, right):
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right))


class VectorStore:
    """Long-term semantic memory (RAG vector index interface)."""

    def __init__(
        self,
        storage_path: str = "./data/vector_index.json",
        model_name: str = DEFAULT_MODEL_NAME,
        embedder=None,
        autoload: bool = True,
    ):
        self.storage_path = storage_path
        self.model_name = model_name
        self._documents = {}
        self._vectors = {}
        self._embedder = embedder
        self._backend_error = ""
        if autoload:
            self.load()

    # ---------------------------------------------------------------- backend
    def _resolve_embedder(self):
        """Returns the active embedder, falling back to hashing when needed."""
        if self._embedder is not None:
            return self._embedder
        try:
            self._embedder = SentenceTransformerEmbedder(self.model_name)
        except Exception as e:  # optional dependency, model download, or OOM
            self._backend_error = str(e)
            self._embedder = HashingEmbedder()
        return self._embedder

    @property
    def backend(self) -> str:
        """Name of the embedding backend in use."""
        return self._resolve_embedder().kind

    def _embed(self, text: str):
        return self._resolve_embedder().encode(text)

    # ------------------------------------------------------------------- write
    def add_document(self, doc_id: str, text: str, metadata: dict = None):
        """Adds or replaces a document in the semantic index."""
        if not doc_id or not str(doc_id).strip():
            return "Vector Store Error: doc_id must be a non-empty string."
        if text is None or not str(text).strip():
            return "Vector Store Error: document text must be non-empty."

        key = str(doc_id)
        self._documents[key] = {"text": str(text), "metadata": dict(metadata or {})}
        self._vectors[key] = self._embed(text)
        return f"Document {key} indexed successfully."

    def clear(self):
        """Removes every document from the index."""
        self._documents.clear()
        self._vectors.clear()
        return "Vector store cleared."

    # -------------------------------------------------------------------- read
    def search(self, query: str, top_k: int = 3):
        """Returns the ``top_k`` most similar documents, best match first."""
        if not self._documents:
            return []
        try:
            top_k = max(1, int(top_k))
        except (TypeError, ValueError):
            top_k = 3

        query_vector = self._embed(query)
        scored = []
        for doc_id, record in self._documents.items():
            vector = self._vectors.get(doc_id)
            if vector is None:
                vector = self._vectors[doc_id] = self._embed(record["text"])
            scored.append((_cosine(query_vector, vector), doc_id, record))

        scored.sort(key=lambda item: (-item[0], item[1]))
        return [
            {
                "doc_id": doc_id,
                "text": record["text"],
                "metadata": record["metadata"],
                "score": round(score, 6),
            }
            for score, doc_id, record in scored[:top_k]
        ]

    def get_document(self, doc_id: str):
        """Returns a stored document record, or None when absent."""
        record = self._documents.get(str(doc_id))
        if record is None:
            return None
        return {"doc_id": str(doc_id), **record}

    def __len__(self):
        return len(self._documents)

    # ------------------------------------------------------------- persistence
    def save(self) -> str:
        """Persists the index (text plus vectors) to ``storage_path``."""
        embedder = self._resolve_embedder()
        payload = {
            "version": STORAGE_VERSION,
            "embedder_kind": embedder.kind,
            "model_name": getattr(embedder, "model_name", self.model_name),
            "dimension": getattr(embedder, "dimension", None),
            "documents": [
                {
                    "doc_id": doc_id,
                    "text": record["text"],
                    "metadata": record["metadata"],
                    "embedding": self._vectors.get(doc_id),
                }
                for doc_id, record in self._documents.items()
            ],
        }
        try:
            directory = os.path.dirname(os.path.abspath(self.storage_path))
            os.makedirs(directory, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
            return f"Vector index saved to {self.storage_path} ({len(self._documents)} documents)."
        except Exception as e:
            return f"Vector Store Save Error: {e}"

    def load(self) -> str:
        """Loads the index, recomputing vectors when the backend changed."""
        if not os.path.exists(self.storage_path):
            return "No existing vector index found."
        try:
            with open(self.storage_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as e:
            return f"Vector Store Load Error: {e}"

        embedder = self._resolve_embedder()
        stored_kind = payload.get("embedder_kind")
        stored_dimension = payload.get("dimension")
        reusable = (
            stored_kind == embedder.kind
            and stored_dimension == getattr(embedder, "dimension", None)
        )

        self._documents.clear()
        self._vectors.clear()
        for entry in payload.get("documents", []):
            doc_id = str(entry.get("doc_id"))
            text = entry.get("text", "")
            self._documents[doc_id] = {"text": text, "metadata": entry.get("metadata") or {}}
            embedding = entry.get("embedding")
            if reusable and embedding:
                self._vectors[doc_id] = embedding
            else:
                self._vectors[doc_id] = self._embed(text)

        note = "" if reusable else " (vectors recomputed for the active backend)"
        return f"Vector index loaded: {len(self._documents)} documents{note}."
