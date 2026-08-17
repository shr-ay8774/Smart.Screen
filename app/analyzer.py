import re
from typing import Dict, List, Tuple

COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "react", "next.js",
    "node.js", "express", "fastapi", "django", "flask", "spring boot",
    "sql", "mysql", "postgresql", "mongodb", "redis", "docker",
    "kubernetes", "aws", "azure", "gcp", "git", "github", "rest api",
    "graphql", "machine learning", "deep learning", "nlp",
    "natural language processing", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "power bi", "tableau", "excel",
    "data analysis", "data analytics", "figma", "tailwind css", "html",
    "css", "c++", "c#", "php", "linux", "kafka", "microservices", "llm",
    "generative ai"
]

DEGREE_TERMS = [
    "b.tech", "btech", "b.e", "be ", "m.tech", "mtech", "mca", "bca",
    "mba", "b.sc", "m.sc", "bachelor", "master", "phd"
]

POSITIVE = [
    "lead", "led", "built", "developed", "implemented", "optimized",
    "deployed", "designed", "automated"
]


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9+#.\- ]+", " ", s.lower())


def extract_skills(text: str) -> List[str]:
    normalized = normalize(text)
    return sorted(
        {
            skill
            for skill in COMMON_SKILLS
            if skill in normalized
        }
    )


def extract_years(text: str) -> float:
    normalized = normalize(text)
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)?",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
    ]
    values = []
    for pattern in patterns:
        values.extend(float(x) for x in re.findall(pattern, normalized))
    return max(values) if values else 0.0


def extract_email(text: str) -> str:
    match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = re.search(r"(?:\+?\d[\d\s().-]{8,}\d)", text)
    return match.group(0).strip() if match else ""


def infer_name(text: str, filename: str) -> str:
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    if lines:
        candidate = lines[0][:80]
        if "@" not in candidate and len(candidate.split()) <= 5:
            return candidate
    return re.sub(r"[_-]+", " ", filename.rsplit(".", 1)[0]).strip()


def score_candidate(job: str, resume: str) -> Dict:
    job_skills = set(extract_skills(job))
    resume_skills = set(extract_skills(resume))

    matched = sorted(job_skills & resume_skills)
    missing = sorted(job_skills - resume_skills)

    skill_score = (
        len(matched) / len(job_skills) * 100
        if job_skills
        else 0
    )

    job_years = extract_years(job)
    resume_years = extract_years(resume)

    exp_score = (
        100
        if job_years == 0
        else min(resume_years / job_years * 100, 100)
    )

    normalized_resume = normalize(resume)
    degree_score = (
        100
        if any(term in normalized_resume for term in DEGREE_TERMS)
        else 50
    )

    job_words = set(
        re.findall(
            r"[a-z][a-z0-9+#.-]{2,}",
            normalize(job)
        )
    )
    resume_words = set(
        re.findall(
            r"[a-z][a-z0-9+#.-]{2,}",
            normalize(resume)
        )
    )

    keyword_score = min(
        100,
        len(job_words & resume_words) / max(1, len(job_words)) * 100,
    )

    action_count = sum(
        normalized_resume.count(word)
        for word in POSITIVE
    )
    impact_score = min(100, 55 + action_count * 5)

    overall = round(
        0.45 * skill_score
        + 0.20 * exp_score
        + 0.15 * keyword_score
        + 0.10 * degree_score
        + 0.10 * impact_score,
        2,
    )

    return {
        "score": overall,
        "skill_score": round(skill_score, 2),
        "experience_score": round(exp_score, 2),
        "semantic_score": round(keyword_score, 2),
        "education_score": round(degree_score, 2),
        "impact_score": round(impact_score, 2),
        "matched_skills": matched,
        "missing_skills": missing,
        "resume_years": resume_years,
        "required_years": job_years,
    }


def rank_candidates(
    job: str,
    resumes: List[Tuple[str, str]]
) -> List[Dict]:
    results = []

    for filename, text in resumes:
        meta = score_candidate(job, text)

        results.append({
            "candidate": infer_name(text, filename),
            "filename": filename,
            "email": extract_email(text),
            "phone": extract_phone(text),
            "resume_text": text,
            **meta,
        })

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True,
    )
