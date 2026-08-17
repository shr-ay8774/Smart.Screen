import ollama

MODEL_NAME = "llama3.2"


def _resolve_model(args):
    for value in reversed(args):
        if isinstance(value, str) and value.strip():
            if " " not in value.strip() and len(value.strip()) <= 100:
                return value.strip()
    return MODEL_NAME


def ollama_available(model=None, *args):
    selected_model = model or _resolve_model(args) or MODEL_NAME

    try:
        response = ollama.list()

        if hasattr(response, "models"):
            models = response.models
            for item in models:
                available_model = getattr(item, "model", "")
                if (
                    available_model == selected_model
                    or available_model.startswith(selected_model + ":")
                ):
                    return True

        elif isinstance(response, dict):
            for item in response.get("models", []):
                available_model = item.get("name", item.get("model", ""))
                if (
                    available_model == selected_model
                    or available_model.startswith(selected_model + ":")
                ):
                    return True

        return False
    except Exception:
        return False


def generate_ai_response(prompt, model=None, *args):
    selected_model = model or _resolve_model(args) or MODEL_NAME

    try:
        response = ollama.chat(
            model=selected_model,
            messages=[{"role": "user", "content": str(prompt)}],
        )

        if hasattr(response, "message"):
            message = response.message
            content = getattr(message, "content", None)
            if content is not None:
                return content

        if isinstance(response, dict):
            return response.get("message", {}).get("content", str(response))

        return str(response)
    except Exception as e:
        return f"AI Error: {e!s}"


def candidate_analysis(resume_text, job_description, *args, model=None):
    selected_model = model or _resolve_model(args)
    prompt = f"""
You are an AI recruitment assistant.

Analyze the candidate's resume against the provided job description.

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
10. Recommendation: Strongly Recommended, Recommended, Consider, or Not Recommended
11. Reason

Do not invent information. Use only the resume and job description.
Be objective.
"""
    return generate_ai_response(prompt, selected_model)


def interview_questions(resume_text, job_description, *args, model=None):
    selected_model = model or _resolve_model(args)
    prompt = f"""
You are an experienced technical recruiter.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

Generate 5 questions for each category:
1. General
2. Technical
3. Resume-Based
4. Behavioral
5. Role-Specific

For every question, explain what the interviewer should evaluate.
Do not invent projects or experience.
"""
    return generate_ai_response(prompt, selected_model)


def ranking_explanation(
    candidate_name,
    candidate_score,
    job_description,
    resume_text,
    *args,
    model=None,
):
    selected_model = model or _resolve_model(args)

    extra = list(args)
    rank = None
    extra_text = []

    for value in extra:
        if isinstance(value, (int, float)):
            rank = value
        elif isinstance(value, str) and value.strip():
            if value.strip() != selected_model:
                extra_text.append(value)

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

Choose the final recommendation from:
- Strongly Recommended
- Recommended
- Consider
- Not Recommended

Do not invent information.
Base the explanation only on the resume and job description.
"""
    return generate_ai_response(prompt, selected_model)


def skill_gap_analysis(
    resume_text,
    job_description,
    *args,
    model=None,
):
    selected_model = model or _resolve_model(args)

    candidate_name = None
    for value in args:
        if isinstance(value, str) and value.strip() != selected_model:
            candidate_name = value
            break

    candidate_text = (
        f"Candidate Name: {candidate_name}"
        if candidate_name
        else ""
    )

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
    return generate_ai_response(prompt, selected_model)


def resume_summary(resume_text, *args, model=None):
    selected_model = model or _resolve_model(args)
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
"""
    return generate_ai_response(prompt, selected_model)


def job_description_analysis(job_description, *args, model=None):
    selected_model = model or _resolve_model(args)
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
"""
    return generate_ai_response(prompt, selected_model)


def candidate_recommendation(
    resume_text,
    job_description,
    candidate_score=None,
    *args,
    model=None,
):
    selected_model = model or _resolve_model(args)
    score_text = (
        f"Current match score: {candidate_score}%"
        if candidate_score is not None
        else "No existing match score was provided."
    )

    prompt = f"""
You are an expert recruitment decision assistant.

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

Choose:
- Strongly Recommended
- Recommended
- Consider
- Not Recommended

Do not invent information.
"""
    return generate_ai_response(prompt, selected_model)


def full_candidate_evaluation(
    resume_text,
    job_description,
    *args,
    model=None,
):
    selected_model = model or _resolve_model(args)

    return {
        "analysis": candidate_analysis(
            resume_text,
            job_description,
            model=selected_model,
        ),
        "interview_questions": interview_questions(
            resume_text,
            job_description,
            model=selected_model,
        ),
        "skill_gap": skill_gap_analysis(
            resume_text,
            job_description,
            model=selected_model,
        ),
    }


if __name__ == "__main__":
    print("Checking Ollama...")
    if ollama_available():
        print(f"Ollama is available with model: {MODEL_NAME}")
    else:
        print(
            f"Ollama is unavailable or model "
            f"'{MODEL_NAME}' is not installed."
        )
