# Medical Prediction & RAG Service

An ML and Retrieval-Augmented Generation (RAG) service that combines supervised machine learning with WHO-grounded medical knowledge retrieval.

The service provides two core capabilities:

1. **Disease prediction** from reported symptoms using a trained Scikit-learn model.
2. **Medical knowledge retrieval and Q&A** using WHO documentation and a multi-provider LLM fallback pipeline.

The functionality is exposed through a **FastAPI backend**, allowing the main application to consume the ML and RAG capabilities through HTTP APIs.

Built from first principles as a deep-dive into production ML, API integration, and LLM/RAG systems.

---

## How It Works

### 1. Symptom-Based Disease Prediction

```text
Symptoms
   │
   ▼
┌─────────────────────────┐
│   FastAPI Prediction    │
│        Endpoint         │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Preprocessing         │
│   + Feature Engineering │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Scikit-learn Model    │
└────────────┬────────────┘
             │
             ▼
Predicted disease
+ confidence
+ recommendations
```

The trained ML model receives the reported symptoms, applies the required preprocessing and feature transformations, and returns a predicted condition together with the associated confidence and recommendations.

---

### 2. RAG-Powered Medical Q&A

```text
User Question
      │
      ▼
┌─────────────────────────┐
│      FastAPI RAG        │
│       Endpoint          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      RAG Pipeline       │
│                         │
│ • LangChain             │
│ • HuggingFace Embeddings│
│ • Qdrant Vector Store   │
│ • WHO Fact Sheets       │
│ • Response Cache        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Multi-provider LLM      │
│ fallback chain          │
│                         │
│ Gemini → Groq →         │
│ Cohere → Mistral        │
└────────────┬────────────┘
             │
             ▼
WHO-grounded response
```

The RAG pipeline retrieves relevant information from indexed WHO documentation before generating a response.

The LLM layer uses a provider fallback chain. If the primary provider fails or reaches a rate limit, the pipeline can fall through to the next configured provider.

These two flows are independent: the disease prediction model does not feed directly into the RAG pipeline, and the RAG pipeline does not modify the ML prediction.

---

## Features

* **Disease prediction** from reported symptoms using a trained Scikit-learn classifier
* **Medicine and precaution recommendations** associated with predicted conditions
* **RAG-grounded medical Q&A** using indexed WHO documentation
* **Semantic retrieval** using HuggingFace embeddings and Qdrant
* **Response caching** to avoid redundant LLM calls for repeated queries
* **Multi-provider LLM fallback** across Gemini, Groq, Cohere, and Mistral
* **FastAPI REST API** for integration with the main application
* **Interactive Swagger UI** for API development and testing
* **Unit and integration tests**

---

## Tech Stack

| Category          | Tools                         |
| ----------------- | ----------------------------- |
| Language          | Python                        |
| ML                | Scikit-learn, Pandas, NumPy   |
| RAG orchestration | LangChain                     |
| Embeddings        | HuggingFace                   |
| Vector store      | Qdrant                        |
| LLM               | Gemini, Groq, Cohere, Mistral |
| API               | FastAPI                       |
| Testing           | Pytest                        |
| Containerization  | Docker                        |

---

## Project Structure

```text
├── data/
│   └── Raw, processed, and interim datasets
│
├── notebooks/
│   └── EDA and experimentation
│
├── src/
│   └── Modular ML and RAG pipeline source code
│
├── artifacts/
│   └── Encoders, scalers, and other generated artifacts
│
├── models/
│   └── Trained ML models
│
├── api/
│   └── FastAPI application and API endpoints
│
├── config/
│   └── Configuration and hyperparameters
│
├── deployment/
│   └── Docker and CI/CD configuration
│
├── tests/
│   └── Unit and integration tests
│
├── .devcontainer/
│   └── Containerized development environment
│
├── pipeline.py
├── requirements.txt
└── README.md
```

---

## Setup

### Clone the Repository

```bash
git clone https://github.com/Edduh20/TibaFlow-Hospital-Management-System.git
cd TibaFlow-Hospital-Management-System
```

### Create the Environment

```bash
conda create -n medrag python=3.11
conda activate medrag
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
GROQ_API_KEY=your_api_key_here
COHERE_API_KEY=your_api_key_here
MISTRAL_API_KEY=your_api_key_here
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_api_key_here
```

> **Important:** Never commit `.env` or expose API credentials in the repository.

---

## Build the Knowledge Base

Before using the RAG functionality, the WHO fact sheets must be embedded and indexed into Qdrant.

```bash
python -c "from pipeline import build_index; build_index("data/processed/knowledge_base")"
```

Ensure the Qdrant credentials are correctly configured in `.env` before running the indexing process.

---

# Running the API

Start the FastAPI development server:

```bash
uvicorn api.app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## API Testing

FastAPI provides an interactive Swagger UI for testing the service without requiring the main application's frontend.

Open:

```text
http://127.0.0.1:8000/docs
```

From the Swagger UI, developers can:

* View available endpoints
* Inspect request and response schemas
* Submit test inputs
* Test disease prediction
* Test RAG-based medical Q&A
* Inspect JSON responses
* Verify API integration before connecting the main application

### Alternative API Documentation

FastAPI ReDoc is available at:

```text
http://127.0.0.1:8000/redoc
```

For development and endpoint testing, **Swagger UI (`/docs`) is recommended.**

---

## Running Tests

Run the complete test suite with:

```bash
pytest tests/
```

---

## Development Workflow

The ML/RAG service can be developed and tested independently before being consumed by the main application.

```text
        ML / RAG Service
               │
               ▼
        ┌──────────────┐
        │   FastAPI    │
        │     API      │
        └──────┬───────┘
               │
        ┌──────┴───────┐
        │              │
        ▼              ▼
   Prediction        RAG
    Endpoint       Endpoint
        │              │
        ▼              ▼
    ML Model      Qdrant + LLM
        │              │
        └──────┬───────┘
               │
               ▼
       Main Application
```

Recommended development flow:

```text
1. Start FastAPI
        ↓
2. Open /docs
        ↓
3. Test the required endpoint
        ↓
4. Verify request/response schema
        ↓
5. Integrate the endpoint with the main application
        ↓
6. Run tests
        ↓
7. Commit changes
```

> **Note:** Scripts under `src/` expect to be run from within that directory due to relative path handling.
