# 🚀 SHL Assessment Recommender Agent

An AI-powered recommendation system that helps recruiters select the most suitable SHL assessments based on hiring requirements.

The application understands natural language hiring requests, retrieves relevant SHL assessments using semantic search, and returns structured recommendations with explanations.

---

## ✨ Features

- 🤖 AI-powered assessment recommendations
- 💬 Multi-turn conversation support
- 🔍 Semantic retrieval using FAISS
- 📚 HuggingFace Embeddings
- ⚡ FastAPI REST API
- 🔄 Assessment comparison mode
- ✅ Structured JSON responses
- 🎯 Conversation-aware recommendations
- 🛡️ Out-of-scope query handling

---

# 🏗️ System Architecture

```
                    User Query
                         │
                         ▼
                 FastAPI Backend
                         │
                         ▼
              Query Classification
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
 Recommendation Flow             Comparison Flow
         │                               │
         ▼                               ▼
     FAISS Retriever              Exact Assessment Match
         │                               │
         ▼                               ▼
  Relevant SHL Assessments        Selected Assessments
         │                               │
         └───────────────┬───────────────┘
                         ▼
                 Large Language Model
                         ▼
               Structured JSON Response
```

---

# 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| Language | Python |
| LLM | OpenRouter |
| Framework | LangChain |
| Embeddings | BAAI/bge-small-en-v1.5 |
| Vector Database | FAISS |
| Data Source | SHL Product Catalog |

---

# 📂 Project Structure

```
SHL_agent/
│
├── app.py
├── main.py
├── config.py
├── pyproject.toml
│
├── data/
│   └── shl_catalog.json
│
├── embeddings/
│   ├── build_index.py
│   └── faiss_index/
│
├── models/
│   └── schemas.py
│
├── services/
│   ├── agent.py
│   ├── comparer.py
│   ├── llm.py
│   ├── prompts.py
│   ├── retriever.py
│   └── router.py
│
└── tests/
```

---

# ⚙️ How It Works

### 1. User sends a hiring request

Example

```
Recommend assessments for a Python Developer.
```

---

### 2. Query Classification

The request is classified into one of the supported tasks:

- Recommendation
- Assessment Comparison
- Out-of-Scope Detection

---

### 3. Semantic Retrieval

Relevant SHL assessments are retrieved from a FAISS vector database using HuggingFace embeddings.

---

### 4. LLM Reasoning

The retrieved assessments and conversation history are passed to the LLM, which:

- selects the most relevant assessments
- generates concise explanations
- returns structured JSON

---

### 5. Response

Example

```json
{
  "reply": "Recommended assessments...",
  "recommendations": [
    {
      "name": "Python (New)",
      "url": "...",
      "test_type": "Knowledge & Skills"
    }
  ],
  "end_of_conversation": true
}
```

---

# 📡 API Endpoints

## Health Check

```
GET /health
```

---

## Chat Endpoint

```
POST /chat
```

Example Request

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Recommend assessments for a Data Analyst."
    }
  ]
}
```

---

# 🚀 Running Locally

Clone the repository

```bash
git clone https://github.com/Sanjay123sam456/shl-assessment-recommender-agent.git
```

Install dependencies

```bash
uv sync
```

Build FAISS index

```bash
python embeddings/build_index.py
```

Run the API

```bash
uvicorn main:app --reload
```

Open

```
http://127.0.0.1:8000/docs
```

---

# 🎯 Supported Capabilities

- SHL assessment recommendations
- Assessment comparison
- Multi-turn conversations
- Hiring requirement refinement
- Conversation-aware recommendations
- Exact assessment matching
- Structured JSON responses

---

# 🔮 Future Improvements

- Hybrid Retrieval (BM25 + Dense Retrieval)
- Cross-Encoder Re-ranking
- Learning-to-Rank models
- Personalized recruiter preferences
- Evaluation dashboard
- Deployment monitoring
- Caching layer for faster retrieval

---

# 👨‍💻 Author

**Sanjay**

MCA Graduate (2025)

AI • Machine Learning • Data Science • Generative AI

GitHub:
https://github.com/Sanjay123sam456

---

## ⭐ If you found this project useful, consider giving it a star!
