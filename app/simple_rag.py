from typing import Dict, List

import numpy as np


class SimpleRAG:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.items = []
        self.embeddings = None

    def _load_model(self):
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)

    def make_chunks(self, text: str, size: int = 80) -> List[str]:
        words = text.split()
        return [
            " ".join(words[i:i + size])
            for i in range(0, len(words), size)
        ]

    def add_resumes(self, resumes: List[Dict]):
        self._load_model()
        self.items = []

        for resume in resumes:
            chunks = self.make_chunks(
                resume.get("resume_text", "")
            )

            for number, chunk in enumerate(chunks):
                if chunk.strip():
                    self.items.append({
                        "candidate": resume.get(
                            "candidate",
                            "Unknown Candidate"
                        ),
                        "chunk_number": number + 1,
                        "text": chunk,
                    })

        if self.items:
            self.embeddings = self.model.encode(
                [item["text"] for item in self.items],
                normalize_embeddings=True,
            )
        else:
            self.embeddings = None

        return self

    def retrieve(
        self,
        job_description: str,
        candidate: str = None,
        top_k: int = 5,
    ):
        if not self.items or self.embeddings is None:
            return []

        self._load_model()

        query = self.model.encode(
            [job_description],
            normalize_embeddings=True,
        )[0]

        scores = np.asarray(self.embeddings) @ query
        results = []

        for index in np.argsort(scores)[::-1]:
            item = dict(self.items[int(index)])

            if candidate and item["candidate"] != candidate:
                continue

            item["similarity"] = round(
                float(scores[int(index)]),
                4,
            )

            results.append(item)

            if len(results) >= top_k:
                break

        return results
