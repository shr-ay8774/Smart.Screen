# Smart Resume Screening and Candidate Ranking System

A BTech project for helping a recruiter compare resumes with a given job description.

## Main idea

The application reads resumes, finds relevant skills and experience, and gives each candidate a score. A small RAG module is also included to find relevant parts of a resume for a job description.

## Features

- Upload PDF and DOCX resumes
- Add a job description
- Extract resume text
- Find common technical skills
- Compare required and available skills
- Check experience
- Rank candidates
- Show missing skills
- Retrieve relevant resume sections
- Optional local AI summary using Ollama
- Export results to Excel

## Technologies

- Python
- Streamlit
- PyPDF2
- python-docx
- scikit-learn
- Sentence Transformers
- - Ollama (optional)
- Pandas
- OpenPyXL

## How to run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
streamlit run Main.py
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

## Optional AI feature

The project does not depend on Gemini. If Ollama is installed, a local model can be used for candidate summaries and interview questions.

Example:

```powershell
ollama pull llama3.2
```

The main screening system works without Ollama.

## Project flow

```text
Job Description
      |
      v
Resume Upload
      |
      v
Text Extraction
      |
      v
Skill + Experience Analysis
      |
      v
Candidate Score
      |
      v
Ranking
      |
      v
Relevant Resume Evidence
      |
      v
Optional AI Summary
```

## Project limitation

This is a student project and the scoring method is a baseline. It should be treated as decision support, not as an automatic hiring system. A recruiter should check the original resume before making a final decision.

## Future improvements

- Better resume parsing
- PostgreSQL database
- pgvector
- Login system
- Better skill taxonomy
- More evaluation data
- Recruiter feedback for improving ranking
