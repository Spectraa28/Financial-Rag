# Enterprise Financial RAG Pipeline

A production-grade Retrieval-Augmented Generation (RAG) system designed to accurately parse, index, and query dense financial documents (SEC 10-K filings). 

## 🏗️ Architecture & Stack
* **Parser Layer:** IBM Docling (Layout-aware extraction preserving SEC tables and footnotes).
* **Vector Database:** ChromaDB (Semantic search with metadata filtering).
* **Keyword Index:** BM25 (Exact-match financial terminology).
* **Generation:** Gemini 2.5 Flash-Lite (via modern `google.genai` SDK).
* **Telemetry:** MLflow & Prometheus (Latency and Token monitoring).

## 🚀 Key Engineering Optimizations
1.  **Cold-Start Latency Reduction:** Engineered an eager-caching system utilizing ChromaDB's persistent states, dropping pipeline boot latency from **46 seconds to 3 seconds**.
2.  **Semantic Chunking:** Replaced brittle HTML regex parsing with Docling's `HybridChunker` bound to a 256-token ceiling. Successfully preserved tabular data integrity, preventing financial metrics from being torn across chunk boundaries.

## 📊 Pipeline Evaluation & Metrics (RAGAs)
The pipeline was rigorously evaluated using the **RAGAs framework**, measuring four core dimensions: Faithfulness, Answer Relevance, Context Precision, and Context Recall. 

| Metric | Pre-Migration (BS4) | Post-Migration (Docling) | Impact |
| :--- | :--- | :--- | :--- |
| **Faithfulness** | 0.82 | 0.85 | Maintained high hallucination resistance. |
| **Context Recall** | 0.00 | 1.00 | *Crucial fix for complex tabular queries (e.g., extracting exact par values from SEC tables).* |

**Key ML Engineering Finding:** During early evaluations, the pipeline exhibited high Faithfulness (0.82) despite failing to answer specific financial queries. This exposed a critical blind spot: high Faithfulness can mask severe ingestion corruption. The LLM was accurately summarizing the context it was given, but the context itself was garbage due to flattening HTML tables. Migrating to layout-aware parsing (Docling) fixed the root ingestion issue, bringing Context Recall up to 1.0 on dense tabular queries.

## ⚙️ Quick Start
1. Clone the repository and add your `.env` file with `GEMINI_API_KEY`.
2. Run `docker build -t financial-rag .`
3. Run `docker run -p 8000:8000 financial-rag`
4. Send a POST request to `http://localhost:8000/query`
