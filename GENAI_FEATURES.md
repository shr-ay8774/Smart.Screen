# Generative AI Features

The project uses a local Llama model through Ollama.

## What normal NLP/ML does

The application calculates:
- skill match
- experience match
- semantic/keyword relevance
- candidate score
- candidate ranking

## What RAG does

RAG retrieves the parts of a resume that are most related to the job description.

It uses:
1. Sentence Transformer embeddings
2. Cosine similarity
3. Top relevant resume chunks

## What GenAI does

The retrieved resume information is sent to the local LLM for:

1. AI Candidate Analysis
2. Why This Ranking?
3. Interview Question Generation
4. AI Skill Gap Analysis

The LLM does not calculate the candidate score.

## Setup

Install Ollama and run:

```powershell
ollama pull llama3.2
```

Then start:

```powershell
python -m streamlit run Main.py
```
