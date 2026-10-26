"""StudentHub — FastAPI Production Web API & Microservice.
======================================================
Provides scalable REST endpoints for student records, academic calculations,
dashboard metrics, and CSV reporting.
Supports PostgreSQL persistence via DATABASE_URL with seamless local JSON fallback.
"""

import os
import sys
import csv
import io
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, status, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Ensure root modules are in Python sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from models import Student
from storage import StudentStorage
from student_service import StudentService

app = FastAPI(
    title="StudentHub Academic API",
    description="Enterprise Student Management REST API with academic metrics, PostgreSQL support, and reporting.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage and service
DATABASE_URL = os.getenv("DATABASE_URL")
storage_backend = "JSON"
if DATABASE_URL:
    storage_backend = "PostgreSQL"

service = StudentService(storage=StudentStorage())


# ---------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------
class StudentCreateRequest(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=32, example="STU-101")
    name: str = Field(..., min_length=2, max_length=128, example="Aarav Sharma")
    course: str = Field(..., min_length=1, max_length=128, example="Computer Science")
    marks: float = Field(..., ge=0.0, le=100.0, example=88.5)
    email: Optional[str] = Field("", max_length=128, example="aarav@university.edu")
    phone: Optional[str] = Field("", max_length=32, example="+91 98765 43210")
    enrollment_date: Optional[str] = Field("", max_length=32, example="2026-10-26")


class StudentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=128)
    course: Optional[str] = Field(None, min_length=1, max_length=128)
    marks: Optional[float] = Field(None, ge=0.0, le=100.0)
    email: Optional[str] = Field(None, max_length=128)
    phone: Optional[str] = Field(None, max_length=32)


class StudentResponse(BaseModel):
    student_id: str
    name: str
    course: str
    marks: float
    percentage: float
    grade: str
    status: str
    email: str
    phone: str
    enrollment_date: str


def student_to_response(s: Student) -> Dict[str, Any]:
    return {
        "student_id": s.student_id,
        "name": s.name,
        "course": s.course,
        "marks": round(s.marks, 1),
        "percentage": s.get_percentage(),
        "grade": s.get_grade(),
        "status": s.get_status(),
        "email": s.email or "",
        "phone": s.phone or "",
        "enrollment_date": s.enrollment_date or ""
    }


# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------
@app.get("/health", tags=["Health"])
def health_check():
    """Liveness probe for Render and orchestrators."""
    return {
        "status": "healthy",
        "service": "studenthub-api",
        "version": "1.0.0",
        "storage": storage_backend,
        "total_records": len(service.students)
    }


@app.get("/api/v1/students", response_model=List[StudentResponse], tags=["Students"])
def list_students(
    search: str = Query("", description="Search term matching ID, name, course, or email"),
    course: str = Query("All", description="Filter by course"),
    grade: str = Query("All", description="Filter by grade letter (A+, A, B, C, D, F)"),
    status: str = Query("All", description="Filter by academic status"),
    sort_by: str = Query("id", description="Sort field: id, name, marks, course, grade"),
    reverse: bool = Query(False, description="Sort descending")
):
    """Retrieve students with multi-criteria filtering and sorting."""
    records = service.search_and_filter(
        query=search,
        course_filter=course,
        grade_filter=grade,
        status_filter=status,
        sort_by=sort_by,
        reverse=reverse
    )
    return [student_to_response(s) for s in records]


@app.get("/api/v1/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def get_student(student_id: str):
    """Get single student profile by ID."""
    s = service.get_student_by_id(student_id)
    if not s:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record '{student_id}' not found."
        )
    return student_to_response(s)


@app.post("/api/v1/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(req: StudentCreateRequest):
    """Add a new student record with validation."""
    success, message = service.add_student(
        student_id=req.student_id,
        name=req.name,
        course=req.course,
        marks=req.marks,
        email=req.email or "",
        phone=req.phone or "",
        enrollment_date=req.enrollment_date or ""
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    s = service.get_student_by_id(req.student_id)
    return student_to_response(s)


@app.put("/api/v1/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def update_student(student_id: str, req: StudentUpdateRequest):
    """Update existing student details."""
    success, message = service.update_student(
        student_id=student_id,
        name=req.name,
        course=req.course,
        marks=req.marks,
        email=req.email,
        phone=req.phone
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    s = service.get_student_by_id(student_id)
    return student_to_response(s)


@app.delete("/api/v1/students/{student_id}", tags=["Students"])
def delete_student(student_id: str):
    """Delete a student record permanently."""
    success, message = service.delete_student(student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )
    return {"message": message, "student_id": student_id}


@app.get("/api/v1/students/metrics/summary", tags=["Analytics"])
def get_dashboard_summary():
    """Retrieve aggregate statistics and distributions for Dashboard charts."""
    metrics = service.get_dashboard_metrics()
    # Format recent students
    recent = [student_to_response(s) for s in metrics.get("recent_students", [])]
    metrics["recent_students"] = recent
    return metrics


@app.get("/api/v1/students/export/csv", tags=["Export"])
def export_students_csv():
    """Stream all student records as a downloadable CSV file."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Student ID", "Name", "Course", "Marks", "Percentage",
        "Grade", "Status", "Email", "Phone", "Enrollment Date"
    ])
    for s in service.students:
        writer.writerow([
            s.student_id,
            s.name,
            s.course,
            f"{s.marks:.1f}",
            f"{s.get_percentage()}%",
            s.get_grade(),
            s.get_status(),
            s.email,
            s.phone,
            s.enrollment_date
        ])
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=studenthub_records.csv"}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
