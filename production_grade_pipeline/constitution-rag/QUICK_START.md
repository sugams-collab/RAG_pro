# Quick Start Guide - Constitution-RAG

## 🚀 60-Second Setup

```bash
# Navigate to project
cd /home/cis/windows/sugam/AI/projects/RAG/production_grade_pipeline/constitution-rag

# Install dependencies (first time only)
pip install -r requirements.txt

# Start services
docker-compose up -d

# Ingest PDFs (place in data/raw/ first)
python scripts/ingest.py data/raw/

# Query via CLI
python app/cli.py query "What are fundamental rights?"

# Or open web UI
streamlit run app/streamlit_app.py

# Or start API server
uvicorn src.api.app:app --reload
```

## 📖 Common Commands

### CLI Interface
```bash
# Single query
python app/cli.py query "Your question here" --timings

# Interactive mode
python app/cli.py interactive

# Batch processing
python app/cli.py batch questions.txt --output results.json
```

### API Queries
```bash
# Health check
curl http://localhost:8000/health

# Single query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Article 21?"}'

# Batch queries
curl -X POST http://localhost:8000/api/v1/query/batch \
  -H "Content-Type: application/json" \
  -d '{
    "questions": ["What are fundamental rights?", "What is equality?"]
  }'

# Cache stats
curl http://localhost:8000/api/v1/query/cache/stats

# Performance metrics
curl http://localhost:8000/api/v1/performance/timings

# Similarity search
curl -X POST http://localhost:8000/api/v1/search/similar \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question", "top_k": 10}'
```

### Web Interfaces
```
Streamlit UI:    http://localhost:8501
FastAPI Docs:    http://localhost:8000/docs
Ollama:          http://localhost:11434
```

## 🔧 Configuration

### Key Environment Variables (.env)

```bash
# LLM Settings
LLM_MODEL=minimax-m3:cloud
OLLAMA_HOST=http://localhost:11434
TEMPERATURE=0.0

# Retrieval Settings
HYBRID_TOP_K=25           # Documents retrieved
RERANKER_TOP_K=8          # Final documents
EMBEDDING_BATCH_SIZE=32

# Paths
DATA_DIR=data
CHROMA_DB_PATH=storage/chroma
BM25_INDEX_PATH=storage/bm25.pkl

# API Settings
HOST=0.0.0.0
PORT=8000
```

### Embedding Models
```python
# Fast, accurate
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5

# More accurate but slower
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

# Alternative
EMBEDDING_MODEL=intfloat/e5-large-v2
```

### Reranker Models
```python
# Best for legal documents
RERANKER_MODEL=BAAI/bge-reranker-base
RERANKER_MODEL=BAAI/bge-reranker-large
```

## 📊 Monitoring

### Check System Health
```bash
# API health
curl http://localhost:8000/health

# View logs
docker-compose logs -f rag-app

# Check cache stats
curl http://localhost:8000/api/v1/query/cache/stats

# Performance metrics
curl http://localhost:8000/api/v1/performance/timings
```

### Clear Cache
```bash
# Clear query cache
curl -X POST http://localhost:8000/api/v1/query/cache/clear
```

## 🐛 Troubleshooting

### "Module not found" errors
✅ **Already Fixed** - All import paths corrected
```python
# ✅ Correct paths
from src.embeddings.embedder import EmbeddingService
from src.retrieval.cross_encoder import CrossEncoderReranker
```

### Settings AttributeError
✅ **Already Fixed** - All settings use UPPERCASE
```python
# ✅ Correct
settings.EMBEDDING_MODEL
settings.CHUNK_SIZE
```

### Empty query results
1. Check if PDFs ingested: `ls -la storage/chroma/`
2. Ingest documents: `python scripts/ingest.py data/raw/`
3. Verify Ollama is running: `curl http://localhost:11434/api/tags`

### Ollama connection issues
```bash
# Check if Ollama is running
docker ps | grep ollama

# Restart Ollama
docker-compose restart ollama

# Check Ollama logs
docker-compose logs ollama

# List available models
curl http://localhost:11434/api/tags
```

### High latency
1. Check cache: `curl http://localhost:8000/api/v1/query/cache/stats`
2. Check timings: `curl http://localhost:8000/api/v1/performance/timings`
3. Try batch queries for better throughput

## 📚 File Structure

```
constitution-rag/
├── src/
│   ├── api/              # FastAPI endpoints
│   ├── chunking/         # Text chunking
│   ├── citations/        # Citation formatting ✨
│   ├── core/             # Core models
│   ├── embeddings/       # Embedding service
│   ├── ingestion/        # PDF ingestion
│   ├── llm/              # LLM integration + prompts ✨
│   ├── rag/              # RAG pipeline
│   ├── retrieval/        # Search (hybrid, BM25, reranking)
│   ├── utils/            # Utilities: cache, timer, logger ✨
│   └── vectorstore/      # ChromaDB integration
├── app/
│   ├── api.py            # Extended API endpoints ✨
│   ├── cli.py            # CLI interface ✨
│   └── streamlit_app.py  # Web UI ✨
├── scripts/
│   ├── ingest.py         # Data ingestion
│   └── query.py          # CLI querying
├── data/                 # PDFs and processed data
├── storage/              # ChromaDB and BM25 indices
├── configs/              # Settings and logging
└── FIXES_AND_UPGRADES.md # Detailed upgrade guide

✨ = Recently implemented or fixed
```

## 🎯 Example Workflows

### Workflow 1: Single Query
```bash
# Terminal 1: Start API
uvicorn src.api.app:app --reload

# Terminal 2: Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Article 14?"}'
```

### Workflow 2: Web UI
```bash
# Terminal 1: Start API
docker-compose up

# Terminal 2: Open web UI
streamlit run app/streamlit_app.py

# Browser: http://localhost:8501
```

### Workflow 3: Batch Processing
```bash
# Create questions.txt
cat > questions.txt << EOF
What are fundamental rights?
What is equality before law?
What is Article 21?
EOF

# Process batch
python app/cli.py batch questions.txt --output results.json

# View results
cat results.json
```

## 💡 Tips & Tricks

1. **Cache queries for faster repeated questions**
   - Cache is automatic, see stats: `curl http://localhost:8000/api/v1/query/cache/stats`

2. **Use batch queries for better throughput**
   - Send multiple questions at once instead of one by one

3. **Monitor performance**
   - Check timings: `curl http://localhost:8000/api/v1/performance/timings`
   - Identify bottlenecks

4. **Format citations differently**
   - In Streamlit: Change "Citation Format" dropdown
   - In API responses: Use different formatter methods

5. **Stream long queries**
   - Use `/api/v1/query/stream` endpoint for real-time response

## 📞 Quick Help

```bash
# See all CLI options
python app/cli.py --help

# API documentation
http://localhost:8000/docs

# Get model info
curl http://localhost:8000/api/v1/models/info

# Full system stats
curl http://localhost:8000/api/v1/stats
```

---

**For detailed information, see:**
- `COMPLETE_ANALYSIS.md` - Full analysis
- `FIXES_AND_UPGRADES.md` - Upgrade recommendations
- `README.md` - Project overview
