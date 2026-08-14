"""Offline-first Zepto policy RAG service.

By default (MOCK_LLM unset or 1) no network request is made.  Chroma and the
sentence-transformers embedding model still run locally for policy retrieval.
"""
from __future__ import annotations

import json
import os
import re
import hashlib
import urllib.request
from pathlib import Path
from typing import Literal, TypedDict

import chromadb
import numpy as np
from fastapi import FastAPI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

from prompt import STRUCTURED_PROMPT

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / ".chroma"
COLLECTION_NAME = "zepto_policy_chunks"
POLICY_KEYWORDS = ("delivery", "return", "refund", "membership", "tracking", "cancel", "gift card", "support hours")
MOCK_DIRECT_ANSWER = "I can only answer questions about Zepto policies right now."


class AskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float = Field(ge=0, le=1)


class AssistantState(TypedDict, total=False):
    query: str
    intent: Literal["policy_question", "general_question"]
    retrieved: list[dict[str, str]]
    response: AskResponse


def mock_mode() -> bool:
    return os.getenv("MOCK_LLM", "1") != "0"


class PolicyStore:
    """Creates the local MiniLM embeddings and persistent Chroma collection."""

    def __init__(self) -> None:
        # Docker preloads these weights.  The fallback keeps the mock baseline
        # usable in a deliberately air-gapped development environment.
        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        except Exception:
            self.model = OfflineFallbackEmbedder()
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )
        self._ingest_if_needed()

    def _ingest_if_needed(self) -> None:
        documents = sorted(DOCS_DIR.glob("doc_*.txt"))
        if len(documents) != 8:
            raise RuntimeError("Expected exactly 8 policy documents in docs/")
        expected_ids = [doc.stem for doc in documents]
        existing = set(self.collection.get(ids=expected_ids)["ids"])
        missing = [doc for doc in documents if doc.stem not in existing]
        if missing:
            texts = [doc.read_text(encoding="utf-8").strip() for doc in missing]
            vectors = self.model.encode(texts, normalize_embeddings=True).tolist()
            self.collection.add(
                ids=[doc.stem for doc in missing], documents=texts,
                metadatas=[{"document_id": doc.stem} for doc in missing], embeddings=vectors,
            )

    def search(self, query: str, limit: int = 3) -> list[dict[str, str]]:
        vector = self.model.encode([query], normalize_embeddings=True).tolist()
        result = self.collection.query(query_embeddings=vector, n_results=limit)
        return [
            {"id": chunk_id, "text": text}
            for chunk_id, text in zip(result["ids"][0], result["documents"][0])
        ]


class OfflineFallbackEmbedder:
    """Small deterministic contingency when MiniLM weights are not cached.

    It is intentionally used only when loading the required local MiniLM model
    fails. Its token hashing keeps the no-network mock demonstration runnable.
    """
    dimensions = 2048
    stopwords = {"a", "an", "and", "are", "can", "for", "how", "i", "in", "is", "it", "of", "on", "the", "to", "what", "when", "with"}

    def encode(self, texts: list[str], normalize_embeddings: bool = True) -> np.ndarray:
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for word in re.findall(r"[a-z0-9]+", text.lower()):
                if word in self.stopwords:
                    continue
                index = int.from_bytes(hashlib.sha256(word.encode()).digest()[:4], "big") % self.dimensions
                vector[index] += 1.0
            magnitude = sum(value * value for value in vector) ** 0.5 or 1.0
            vectors.append([value / magnitude for value in vector])
        return np.array(vectors, dtype=np.float32)


_store: PolicyStore | None = None


def get_store() -> PolicyStore:
    global _store
    if _store is None:
        _store = PolicyStore()
    return _store


def call_real_llm(prompt: str) -> str:
    """Optional Groq OpenAI-compatible call; never reached in default mock mode."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("MOCK_LLM=0 requires GROQ_API_KEY")
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps({"model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"), "messages": [{"role": "user", "content": prompt}], "temperature": 0}).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310: fixed HTTPS endpoint
        return json.loads(response.read())["choices"][0]["message"]["content"]


def validated_real_answer(prompt: str) -> AskResponse:
    """Validate and correct optional LLM JSON, retrying twice on bad output."""
    correction = "\nYour previous response was invalid. Return ONLY valid JSON matching the requested schema."
    last_error = "unknown validation error"
    for attempt in range(3):
        try:
            return AskResponse.model_validate_json(call_real_llm(prompt + (correction if attempt else "")))
        except Exception as exc:
            last_error = str(exc)
    return AskResponse(answer=f"ERROR: real LLM response failed schema validation: {last_error}", sources=[], confidence=0.0)


def classify_intent(state: AssistantState) -> AssistantState:
    query = state["query"]
    if mock_mode():
        intent: Literal["policy_question", "general_question"] = (
            "policy_question" if any(word in query.lower() for word in POLICY_KEYWORDS) else "general_question"
        )
    else:
        raw = call_real_llm(f"Classify this query as exactly policy_question or general_question: {query}").strip().lower()
        intent = "policy_question" if "policy_question" in raw else "general_question"
    return {"intent": intent}


def retrieve_and_answer(state: AssistantState) -> AssistantState:
    chunks = get_store().search(state["query"], limit=3)
    if mock_mode():
        snippet = chunks[0]["text"][:200]
        response = AskResponse(answer=f"Based on the retrieved context: {snippet}", sources=[c["id"] for c in chunks], confidence=1.0)
    else:
        context = "\n\n".join(f"[{c['id']}] {c['text']}" for c in chunks)
        response = validated_real_answer(STRUCTURED_PROMPT.format(context=context, query=state["query"]))
    return {"retrieved": chunks, "response": response}


def direct_answer(state: AssistantState) -> AssistantState:
    if mock_mode():
        response = AskResponse(answer=MOCK_DIRECT_ANSWER, sources=[], confidence=1.0)
    else:
        response = validated_real_answer(STRUCTURED_PROMPT.format(context="No policy context was retrieved.", query=state["query"]))
    return {"response": response}


def route_by_intent(state: AssistantState) -> str:
    return "retrieve_and_answer" if state["intent"] == "policy_question" else "direct_answer"


builder = StateGraph(AssistantState)
builder.add_node("classify_intent", classify_intent)
builder.add_node("retrieve_and_answer", retrieve_and_answer)
builder.add_node("direct_answer", direct_answer)
builder.add_edge(START, "classify_intent")
builder.add_conditional_edges("classify_intent", route_by_intent, {"retrieve_and_answer": "retrieve_and_answer", "direct_answer": "direct_answer"})
builder.add_edge("retrieve_and_answer", END)
builder.add_edge("direct_answer", END)
graph = builder.compile()

app = FastAPI(title="Zepto Support Assistant")


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    result = graph.invoke({"query": request.query})
    return result["response"]
