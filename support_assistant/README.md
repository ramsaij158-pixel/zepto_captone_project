# Zepto Support Assistant

An offline-first RAG service for Zepto policy questions. `MOCK_LLM` is enabled by default: leave it unset (or set `MOCK_LLM=1`) to make the complete, deterministic flow run without an API key or an LLM network call.

## Run locally

```bash
cd support_assistant
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

The first request loads the local `all-MiniLM-L6-v2` sentence-transformers model and creates the persistent Chroma database in `.chroma/`. The Docker build preloads those model weights so serving needs no model-provider network call. In an intentionally air-gapped developer machine where the weights were never cached, the app uses a deterministic token-vector contingency so the mock demonstration remains runnable; normal local/Docker usage uses MiniLM.

```bash
curl -s -X POST http://127.0.0.1:7860/ask -H 'content-type: application/json' -d '{"query":"What is the delivery fee?"}'
curl -s -X POST http://127.0.0.1:7860/ask -H 'content-type: application/json' -d '{"query":"What is the capital of France?"}'
```

Example mock-mode JSON responses (the first snippet is deterministically drawn from the top retrieved chunk):

```json
{"answer":"Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del","sources":["doc_01","doc_04","doc_03"],"confidence":1.0}
```

```json
{"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}
```

## Terminal output snapshot

```bash
$ curl -s -X POST http://127.0.0.1:7860/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"When is Zepto standard delivery free?"}' | python -m json.tool
{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard delivery is free on orders over INR 149; orders below this threshold incur a flat INR 25 delivery fee.",
  "sources": [
    "doc_01",
    "doc_04",
    "doc_03"
  ],
  "confidence": 1.0
}

$ curl -s -X POST http://127.0.0.1:7860/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the capital of France?"}' | python -m json.tool
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```

## Architecture

```text
docs/doc_01.txt ... doc_08.txt
       | ingestion + per-document chunking (PolicyStore._ingest_if_needed)
       v
all-MiniLM-L6-v2 local embeddings --> Chroma collection: zepto_policy_chunks
       |                                         |
POST /ask --> classify_intent --> policy_question --> retrieve_and_answer --> JSON
                  |                    (top-3 cosine retrieval)                 
                  +--> general_question --> direct_answer ---------------------->
```

1. **Ingestion:** `PolicyStore._ingest_if_needed` reads the eight corpus files; each complete document is one chunk with its `doc_XX` ID.
2. **Embedding:** that same component uses the local `all-MiniLM-L6-v2` model and persists the vectors in Chroma collection `zepto_policy_chunks` with cosine similarity.
3. **Retrieval:** the LangGraph `retrieve_and_answer` node embeds a policy query and fetches the top three chunks from Chroma.
4. **Generation:** `classify_intent` routes to `retrieve_and_answer` or `direct_answer`. In mock mode, they construct deterministic answers and Pydantic validates `answer`, `sources`, and `confidence`. The optional real path uses the actual role–context–task–format–length prompt in `prompt.py`, including a negative constraint and few-shot example. Invalid real-LLM JSON is retried twice with a correction before returning a marked error response.

Every generation point branches on `MOCK_LLM`: default mock mode uses the specified keyword classifier, retrieved-context template, and fixed direct response without LLM calls. With `MOCK_LLM=0`, the optional Groq-compatible implementation makes real LLM calls (requiring `GROQ_API_KEY`); embedding and Chroma retrieval remain local in both modes.

## Docker

```bash
cd support_assistant
docker build -t zepto-support .
docker run --rm -p 7860:7860 zepto-support
```

Then send the same `POST /ask` calls to `http://127.0.0.1:7860/ask`. The image serves mock mode by default.
