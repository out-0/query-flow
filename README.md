# 📡 Query-Flow

# OVERVIEW

This project takes a search query like `"What is python"` and turns it into **clean, ranked web content**.

Instead of just showing links like Google, it:

```text
query → search engine → web pages → cleaned text → filtering → ranking → final results
```

Think of it as a **mini search pipeline for an AI agent**.

---

# 🧠 What this project is

Query-Flow is a **modular web retrieval system** built to feed an AI agent with real web content.

It replaces paid search APIs by using:

- SearXNG (local or public instances)
- Direct web scraping
- Custom ranking system

It is NOT:
- a production search engine
- a polished API service
- a crawler network

It is:
> a learning + practical retrieval pipeline for AI assistants

---

# 🏗 Architecture

```text
User Query
   ↓
app.py (orchestrator)
   ↓
SearXNG Provider (local → fallback public)
   ↓
fetch_layer (download HTML pages)
   ↓
extraction_layer (extract readable text)
   ↓
filtering_layer (remove junk pages)
   ↓
ranking_layer (score relevance)
   ↓
output_layer (display results)
```

# 📋 Prerequisites

Before running, ensure you have the following installed:
- **Docker & Docker Compose**: To run the local SearXNG instance.
- **Python 3.10+**: The core application language.
- **uv** (recommended) or **pip**: For dependency management.
- **make**: (Optional) For using the provided shortcut commands.

---

# 🔄 Core Pipeline

## 1. Search Layer
Uses SearXNG:

- Local Docker instance (preferred)
- Public fallback instances (if local fails)

Handles routing automatically.

---

## 2. Fetch Layer
Downloads raw HTML using `httpx`.

Problem:
- Some sites block bots (Wikipedia, StackOverflow, Canva, etc.)
- 403 errors are expected, not fatal

Fix used:
- Browser-like headers
- Redirect support

---

## 3. Extraction Layer
Uses `trafilatura` to extract readable content from HTML.

Removes:
- navigation
- ads
- cookie banners

---

## 4. Filtering Layer
Removes:
- empty documents
- very short pages
- low-quality content

---

## 5. Ranking Layer
Scores documents using:

- keyword matching
- simple IDF weighting
- title vs body weighting
- repetition penalty
- spam detection

Output is a ranked list of documents.

---

## 6. Output Layer
Prints:

- score
- title (best-effort)
- preview text
- keyword matches

---

# ⚙️ Configuration

Inside `config.py`:

- `MAX_SEARCH_RESULTS` → limits crawling
- `HTTP_TIMEOUT` → request timeout
- ranking weights (title, body, spam, etc.)

---

# 🐳 Running the project

## Start SearXNG (required)

```bash
make docker_start
```

or:

```bash
docker compose up -d
```

## Run pipeline

```bash
python app.py
```

---

# ⚠️ Known issues

## 1. Some websites block scraping
Examples:
- Wikipedia
- StackOverflow
- Canva

Reason:
- bot protection (403 Forbidden)

This is normal.

---

## 2. HTML structure is inconsistent
SearXNG instances differ slightly, so results may vary.

---

## 3. Ranking is simple
Current ranking is heuristic-based, not ML-based.

So sometimes:
- homepage pages rank high
- noisy pages pass filtering

---

## 4. No async fetching
Requests are sequential → slower performance.

---

# 🧩 Design goal

This project was originally built as part of an **AI terminal agent experiment**.

The goal was:

> Replace paid search APIs with a free, controllable retrieval pipeline.

So it can be plugged into:

- AI chatbots
- local agents
- RAG systems
- terminal assistants

---

# 🚀 Performance Tip

Since the current version uses **sequential fetching**, performance depends on the number of results.
If the pipeline feels slow, you can adjust `MAX_SEARCH_RESULTS` in `config.py` to a lower value (e.g., `3` or `5`) for a much faster response.



# 💡 Why it exists

Because:

- Search APIs are expensive
- Google APIs are limited
- AI needs external context
- SearXNG is free but raw
- raw web data needs processing

So this pipeline sits in the middle.

---

# 🧪 What it teaches

- search engine basics
- data pipelines (ETL style)
- web scraping limitations
- ranking heuristics
- fallback system design
- modular architecture

---

# 🔮 Future improvements (optional)

- async fetch (huge speed boost)
- better metadata preservation
- smarter ranking (semantic scoring)
- optional LLM summarization layer
- structured JSON output API
```
