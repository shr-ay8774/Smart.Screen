from app.database import (
    create_screening,
    initialize_database,
    save_candidate,
)

initialize_database()


job_description = """
Python developer with FastAPI,
PostgreSQL and REST API experience.
"""


screening_id = create_screening(job_description)

print(f"Created screening: {screening_id}")


save_candidate(
    screening_id=screening_id,
    candidate_name="Test Candidate",
    resume_filename="test_resume.pdf",
    match_score=87.5,
    skill_score=90.0,
    experience_score=85.0,
    semantic_score=88.0,
    matched_skills="Python, FastAPI, PostgreSQL",
    missing_skills="Docker",
)

print("Candidate saved successfully.")
