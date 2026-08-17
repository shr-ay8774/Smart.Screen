import os

import requests
from dotenv import load_dotenv

load_dotenv()

LOCAL_MODEL = "llama3.2"
CLOUD_MODEL = "gpt-oss:120b-cloud"

OLLAMA_API_KEY = os.getenv(
    "OLLAMA_API_KEY",
    "",
).strip()

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434",
).strip()

IS_CLOUD = bool(OLLAMA_API_KEY)

MODEL_NAME = CLOUD_MODEL if IS_CLOUD else LOCAL_MODEL


def _resolve_model(args):
    if IS_CLOUD:
        return CLOUD_MODEL

    for value in reversed(args):
        if isinstance(value, str):
            value = value.strip()

            if value and " " not in value and len(value) <= 100:
                return value

    return LOCAL_MODEL


def ollama_available(model=None, *args):
    if IS_CLOUD:
        return bool(OLLAMA_API_KEY)

    selected_model = model or _resolve_model(args)

    try:
        response = requests.get(
            f"{OLLAMA_HOST}/api/tags",
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        for item in data.get(
            "models",
            [],
        ):
            available_model = item.get(
                "name",
                item.get("model", ""),
            )

            if available_model == selected_model or available_model.startswith(
                selected_model + ":"
            ):
                return True

        return False

    except Exception:
        return False


def generate_ai_response(
    prompt,
    model=None,
    *args,
):
    if IS_CLOUD:
        selected_model = CLOUD_MODEL
    else:
        selected_model = model or _resolve_model(args)

    try:
        if IS_CLOUD:
            response = requests.post(
                "https://ollama.com/api/chat",
                headers={
                    "Authorization": (f"Bearer {OLLAMA_API_KEY}"),
                    "Content-Type": ("application/json"),
                },
                json={
                    "model": selected_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": str(prompt),
                        }
                    ],
                    "stream": False,
                },
                timeout=300,
            )

            if not response.ok:
                return (
                    f"Ollama Cloud Error: HTTP {response.status_code}: {response.text}"
                )

        else:
            response = requests.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": selected_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": str(prompt),
                        }
                    ],
                    "stream": False,
                },
                timeout=300,
            )

            if not response.ok:
                return (
                    f"Ollama Local Error: HTTP {response.status_code}: {response.text}"
                )

        data = response.json()

        message = data.get(
            "message",
            {},
        )

        if isinstance(message, dict):
            content = message.get(
                "content",
                "",
            )

            if content:
                return content

        return str(data)

    except requests.exceptions.Timeout:
        return "Ollama Error: The AI request timed out."

    except requests.exceptions.ConnectionError:
        if IS_CLOUD:
            return "Ollama Cloud Error: Could not connect to Ollama Cloud."

        return (
            "Ollama Local Error: "
            "Could not connect to Ollama. "
            "Make sure Ollama is running."
        )

    except Exception as e:
        return f"Ollama Error: {e!s}"


def candidate_analysis(
    resume_text,
    job_description,
    *args,
    model=None,
):
    selected_model = CLOUD_MODEL if IS_CLOUD else (model or _resolve_model(args))

    prompt = f"""
You are an AI recruitment assistant.

Analyze the candidate's resume against
the provided job description.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

Provide:

1. Overall Match Score from 0 to 100
2. Candidate Summary
3. Matching Skills
4. Missing Skills
5. Experience Analysis
6. Education Analysis
7. Projects Analysis
8. Strengths
9. Weaknesses
10. Recommendation

Choose exactly one:

Strongly Recommended
Recommended
Consider
Not Recommended

11. Reason

Do not invent information.
Use only information present in the
resume and job description.
Be objective.
"""

    return generate_ai_response(
        prompt,
        selected_model,
    )


def interview_questions(
    resume_text,
    job_description,
    *args,
    model=None,
):
    selected_model = CLOUD_MODEL if IS_CLOUD else (model or _resolve_model(args))

    prompt = f"""
You are an experienced technical recruiter.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

Generate 5 questions for each category:

1. General Questions
2. Technical Questions
3. Resume-Based Questions
4. Behavioral Questions
5. Role-Specific Questions

For every question provide:

Question:
What the interviewer should evaluate:

Questions must be based only on
the resume and job description.

Do not invent projects, experience,
skills, or achievements.
"""

    return generate_ai_response(
        prompt,
        selected_model,
    )


def ranking_explanation(
    candidate_name,
    candidate_score,
    job_description,
    resume_text,
    *args,
    model=None,
):
    selected_model = CLOUD_MODEL if IS_CLOUD else (model or _resolve_model(args))

    rank = None

    for value in args:
        if isinstance(
            value,
            (int, float),
        ):
            rank = value

    rank_text = f"Candidate Rank: #{rank}" if rank is not None else ""

    prompt = f"""
You are an AI recruitment assistant.

CANDIDATE:
Name: {candidate_name}

MATCH SCORE:
{candidate_score}%

{rank_text}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Explain:

1. Ranking Summary
2. Score Explanation
3. Strongest Matches
4. Missing Requirements
5. Relevant Experience
6. Key Ranking Factors
7. Final Recommendation
8. Interview Consideration

Choose exactly one:

Strongly Recommended
Recommended
Consider
Not Recommended

Do not invent information.
Base the explanation only on the
resume and job description.
"""

    return generate_ai_response(
        prompt,
        selected_model,
    )


def skill_gap_analysis(
    resume_text,
    job_description,
    *args,
    model=None,
):
    selected_model = CLOUD_MODEL if IS_CLOUD else (model or _resolve_model(args))

    candidate_name = None

    for value in args:
        if (
            isinstance(value, str)
            and value.strip()
            and value.strip()
            not in {
                selected_model,
                LOCAL_MODEL,
                CLOUD_MODEL,
            }
        ):
            candidate_name = value.strip()
            break

    candidate_text = f"Candidate Name: {candidate_name}" if candidate_name else ""

    prompt = f"""
You are an AI recruitment assistant.

{candidate_text}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Identify:

1. Matching Skills
2. Missing Skills
3. Partially Matching Skills
4. Priority Skill Gaps
5. Recommendations
6. Overall Skill Assessment

Do not invent information.
Use only the resume and job description.
"""

    return generate_ai_response(
        prompt,
        selected_model,
    )


def resume_summary(
    resume_text,
    *args,
    model=None,
):
    selected_model = CLOUD_MODEL if IS_CLOUD else (model or _resolve_model(args))

    prompt = f"""
You are a professional resume reviewer.

RESUME:
{resume_text}

Provide:

1. Professional Summary
2. Technical Skills
3. Education
4. Work Experience
5. Projects
6. Certifications
7. Key Strengths

Do not invent information.
Use only information present in the resume.
"""

    return generate_ai_response(
        prompt,
        selected_model,
    )


def job_description_analysis(
    job_description,
    *args,
    model=None,
):
    selected_model = CLOUD_MODEL if IS_CLOUD else (model or _resolve_model(args))

    prompt = f"""
You are an expert technical recruiter.

JOB DESCRIPTION:
{job_description}

Extract:

1. Job Role
2. Required Skills
3. Preferred Skills
4. Required Experience
5. Education Requirements
6. Key Responsibilities
7. Important Technologies
8. Candidate Profile
9. Important Keywords

Be concise and accurate.
Do not invent information.
"""

    return generate_ai_response(
        prompt,
        selected_model,
    )


def candidate_recommendation(
    resume_text,
    job_description,
    candidate_score=None,
    *args,
    model=None,
):
    selected_model = CLOUD_MODEL if IS_CLOUD else (model or _resolve_model(args))

    if candidate_score is not None:
        score_text = f"Current match score: {candidate_score}%"
    else:
        score_text = "No existing match score was provided."

    prompt = f"""
You are an expert recruitment
decision assistant.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

SCORE:
{score_text}

Provide:

1. Recommendation
2. Reasoning
3. Top 3 Strengths
4. Top 3 Concerns
5. Final Decision

Choose exactly one:

Strongly Recommended
Recommended
Consider
Not Recommended

Do not invent information.
"""

    return generate_ai_response(
        prompt,
        selected_model,
    )


def full_candidate_evaluation(
    resume_text,
    job_description,
    *args,
    model=None,
):
    selected_model = CLOUD_MODEL if IS_CLOUD else (model or _resolve_model(args))

    return {
        "analysis": candidate_analysis(
            resume_text,
            job_description,
            model=selected_model,
        ),
        "interview_questions": (
            interview_questions(
                resume_text,
                job_description,
                model=selected_model,
            )
        ),
        "skill_gap": skill_gap_analysis(
            resume_text,
            job_description,
            model=selected_model,
        ),
    }


if __name__ == "__main__":
    print("SmartScreen AI")
    print(f"Model: {MODEL_NAME}")

    if IS_CLOUD:
        print("Mode: Ollama Cloud API")
    else:
        print("Mode: Local Ollama")

    if ollama_available():
        print("AI connection is ready.")
    else:
        print("AI connection is unavailable.")
