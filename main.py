from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import json

from rapidfuzz import fuzz

# --------------------
# App setup
# --------------------

app = FastAPI(
    title="Course to Skills API",
    description="Maps course descriptions to canonical course identifiers",
    version="0.2.0"
)

# --------------------
# Load course data (once at startup)
# --------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "WY_highschool_courses_shorter_CUUIDs_machine.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    COURSES = json.load(f)

# --------------------
# Request / Response models
# --------------------

class CourseRequest(BaseModel):
    course_name: str
    course_code: str

class MatchResponse(BaseModel):
    cuuid: Optional[str]
    name_score: float
    code_score: float

# --------------------
# Matching logic
# --------------------

NAME_THRESHOLD = 80.0
CODE_THRESHOLD = 90.0


def find_best_match(course_name: str, course_code: str) -> MatchResponse:
    best_match = None
    best_name_score = 0.0
    best_code_score = 0.0

    for course in COURSES:
        # Match against ALL known aliases
        name_scores = [
            fuzz.token_set_ratio(course_name, name)
            for name in course.get("Names", [])
        ]
        code_scores = [
            fuzz.ratio(course_code, code)
            for code in course.get("Codes", [])
        ]

        if not name_scores or not code_scores:
            continue

        name_score = max(name_scores)
        code_score = max(code_scores)

        # Require BOTH name and code to pass threshold
        if (
            name_score >= NAME_THRESHOLD
            and code_score >= CODE_THRESHOLD
            and (name_score + code_score) > (best_name_score + best_code_score)
        ):
            best_match = course["CUUID"]
            best_name_score = name_score
            best_code_score = code_score

    return MatchResponse(
        cuuid=best_match,
        name_score=best_name_score,
        code_score=best_code_score,
    )

# --------------------
# Routes
# --------------------

@app.get("/")
def root():
    return {"service": "course-skill-mapping", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/course_to_skills", response_model=MatchResponse)
def course_to_skills(request: CourseRequest):
    result = find_best_match(
        course_name=request.course_name,
        course_code=request.course_code,
    )

    if result.cuuid is None:
        raise HTTPException(
            status_code=404,
            detail="No sufficiently confident course match found",
        )

    return result
