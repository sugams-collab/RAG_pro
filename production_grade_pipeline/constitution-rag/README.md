# Hybrid RAG with Hybrid Search, Reranking & Citations

A production-grade Retrieval-Augmented Generation (RAG) system built from scratch.

## Features

- ✅ PDF Ingestion
- ✅ Hybrid Search (Dense + BM25)
- ✅ ChromaDB Vector Database
- ✅ Cross Encoder Reranking
- ✅ Source Citations
- ✅ FastAPI REST API
- ✅ Ollama Support
- ✅ Production Logging
- ✅ Modular Architecture
- ✅ Config Driven
- ✅ Batch Embedding
- ✅ CLI Query Tool

---

# Project Structure

```text
HybridRAG/
│
├── configs/
│   ├── settings.py
│   └── logging.py
│
├── data/
│   ├── raw/
│   ├── chroma/
│   └── bm25/
│
├── scripts/
│   ├── ingest.py
│   └── query.py
│
├── src/
│   ├── api/
│   ├── chunking/
│   ├── core/
│   ├── embedding/
│   ├── ingestion/
│   ├── llm/
│   ├── rag/
│   ├── reranker/
│   ├── retrieval/
│   └── vectorstore/
│
├── requirements.txt
├── .env
└── README.md
```

---

# Installation

Clone the repository.

```bash
git clone <repo-url>

cd HybridRAG
```

Create a virtual environment.

```bash
python -m venv .venv
```

Linux / macOS

```bash
source .venv/bin/activate
```

Windows

```cmd
.venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# Install Ollama

Start Ollama.

```bash
ollama serve
```

Pull your preferred model.

```bash
ollama pull minimax-m3:cloud
```

or

```bash
ollama pull qwen3:8b
```

---

# Add PDFs

```text
data/raw/

    constitution.pdf
```

---

# Ingest Documents

```bash
python scripts/ingest.py \
    --path data/raw
```

The pipeline performs:

```
PDF
    ↓
Loader
    ↓
Parser
    ↓
Cleaner
    ↓
Chunker
    ↓
Embedding
    ↓
ChromaDB
    ↓
BM25
```

---

# Start API

```bash
uvicorn src.api.app:app --reload
```

Swagger UI

```
http://localhost:8000/docs
```

---

# Query using CLI

```bash
python scripts/query.py
```

Example

```
Question >

What is Article 21A?
```

---

# Query using API

POST

```
/query
```

Body

```json
{
    "question":"What is Article 21A?"
}
```

Example Response

```json
{
  "answer": "...",
  "citations": [
    {
      "source": "constitution.pdf",
      "page": 65,
      "article": "21A",
      "score": 0.9912
    }
  ]
}
```

---

# Pipeline

```
                User Query
                     │
                     ▼
             Query Embedding
                     │
                     ▼
        Dense Search (ChromaDB)
                     │
                     │
                     ▼
           Sparse Search (BM25)
                     │
                     ▼
      Reciprocal Rank Fusion (RRF)
                     │
                     ▼
        CrossEncoder Reranker
                     │
                     ▼
          Prompt Construction
                     │
                     ▼
             Ollama LLM
                     │
                     ▼
      Answer + Source Citations
```

---

# Future Improvements

- Hybrid score normalization
- Query expansion
- Multi-query retrieval
- Parent-child retrieval
- Context compression
- Streaming responses
- Redis cache
- Async ingestion
- OCR support
- Multi-document collections
- Metadata filtering
- Evaluation framework
- Unit and integration tests
- Docker support
- Kubernetes deployment
- Monitoring with Prometheus & Grafana

---

# License

MIT License