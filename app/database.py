import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is missing. Set it in .env locally or Railway Variables."
        )

    return psycopg2.connect(database_url)


def initialize_database():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS screenings (
                id SERIAL PRIMARY KEY,
                job_description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS candidates (
                id SERIAL PRIMARY KEY,
                screening_id INTEGER
                    REFERENCES screenings(id)
                    ON DELETE CASCADE,
                candidate_name TEXT,
                resume_filename TEXT,
                match_score REAL,
                skill_score REAL,
                experience_score REAL,
                semantic_score REAL,
                matched_skills TEXT,
                missing_skills TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        connection.commit()
    finally:
        cursor.close()
        connection.close()


def create_screening(job_description):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO screenings (job_description)
            VALUES (%s)
            RETURNING id;
            """,
            (job_description,),
        )

        screening_id = cursor.fetchone()[0]
        connection.commit()
        return screening_id
    finally:
        cursor.close()
        connection.close()


def save_candidate(
    screening_id,
    candidate_name,
    resume_filename,
    match_score,
    skill_score,
    experience_score,
    semantic_score,
    matched_skills,
    missing_skills,
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO candidates (
                screening_id,
                candidate_name,
                resume_filename,
                match_score,
                skill_score,
                experience_score,
                semantic_score,
                matched_skills,
                missing_skills
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                screening_id,
                candidate_name,
                resume_filename,
                match_score,
                skill_score,
                experience_score,
                semantic_score,
                matched_skills,
                missing_skills,
            ),
        )

        connection.commit()
    finally:
        cursor.close()
        connection.close()


def get_screening_history():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                s.id,
                s.job_description,
                s.created_at,
                COUNT(c.id) AS candidate_count
            FROM screenings s
            LEFT JOIN candidates c
                ON c.screening_id = s.id
            GROUP BY s.id, s.job_description, s.created_at
            ORDER BY s.created_at DESC;
            """
        )

        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def get_screening_candidates(screening_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                candidate_name,
                resume_filename,
                match_score,
                skill_score,
                experience_score,
                semantic_score,
                matched_skills,
                missing_skills,
                created_at
            FROM candidates
            WHERE screening_id = %s
            ORDER BY match_score DESC;
            """,
            (screening_id,),
        )

        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def delete_screening(screening_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM screenings
            WHERE id = %s;
            """,
            (screening_id,),
        )

        connection.commit()
    finally:
        cursor.close()
        connection.close()
