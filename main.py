from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Course to Skills API",
    description="Maps course descriptions to a list of skills",
    version="0.1.0"
)

# --------------------
# Request / Response models
# --------------------

class CourseRequest(BaseModel):
    course_name: str

class SkillsResponse(BaseModel):
    skills: List[str]

# --------------------
# Routes
# --------------------

@app.get("/")
def root():
    return {
        "service": "course-skill-mapping",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/course_to_skills", response_model=SkillsResponse)
def course_to_skills(request: CourseRequest):
    # For now, this is hard-coded dummy logic
    # Later, you will replace this with:
    # - similarity matching
    # - embedding lookup
    # - Firestore query

    return SkillsResponse(
        skills=[
            "Algorithms",
            "Data Structures",
            "Databases",
            "Software Engineering"
        ]
    )
