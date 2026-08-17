from io import BytesIO

import pandas as pd


def export_xlsx(results):
    output = BytesIO()
    rows = []

    for result in results:
        rows.append({
            "Candidate": result.get("candidate", ""),
            "Email": result.get("email", ""),
            "Score": result.get("score", 0),
            "Skill Match": result.get("skill_score", 0),
            "Experience": result.get("experience_score", 0),
            "Semantic Match": result.get("semantic_score", 0),
            "Education": result.get("education_score", 0),
            "Matched Skills": ", ".join(
                result.get("matched_skills", [])
            ),
            "Missing Skills": ", ".join(
                result.get("missing_skills", [])
            ),
        })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(rows).to_excel(
            writer,
            index=False,
            sheet_name="Rankings",
        )

    return output.getvalue()
