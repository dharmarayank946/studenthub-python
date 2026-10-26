"""StudentHub — Service & Business Logic Layer.
=============================================
Encapsulates all student record management, validation rules,
search/filtering logic, and academic statistical computations.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from models import Student
from storage import StudentStorage


class StudentService:
    """Business logic service for StudentHub."""

    def __init__(self, storage: Optional[StudentStorage] = None):
        self.storage = storage or StudentStorage()
        self.students: List[Student] = self.storage.load_students()

    def get_existing_ids(self) -> Set[str]:
        """Return a set of all student IDs in uppercase for O(1) duplicate checks.
        
        Demonstrates Data Structure: Sets.
        """
        return {s.student_id.upper() for s in self.students}

    def add_student(
        self,
        student_id: str,
        name: str,
        course: str,
        marks: float,
        email: str = "",
        phone: str = "",
        enrollment_date: str = "",
    ) -> Tuple[bool, str]:
        """Add a new student record after thorough validation."""
        clean_id = str(student_id).strip()
        clean_name = str(name).strip()
        clean_course = str(course).strip()

        # 1. Validate Student ID
        if not clean_id:
            return False, "Student ID cannot be empty."

        if clean_id.upper() in self.get_existing_ids():
            return False, f"A student with ID '{clean_id}' already exists."

        # 2. Validate Name
        if not clean_name:
            return False, "Student name cannot be empty."
        if len(clean_name) < 2:
            return False, "Student name must contain at least 2 characters."

        # 3. Validate Course
        if not clean_course:
            return False, "Course name cannot be empty."

        # 4. Validate Marks
        try:
            m = float(marks)
            if not 0.0 <= m <= 100.0:
                return False, "Marks must be between 0.0 and 100.0."
        except (ValueError, TypeError):
            return False, "Marks must be a valid numerical value."

        student = Student(
            student_id=clean_id,
            name=clean_name,
            course=clean_course,
            marks=m,
            email=email,
            phone=phone,
            enrollment_date=enrollment_date,
        )

        self.students.append(student)
        saved = self.storage.save_students(self.students)
        if not saved:
            return False, "Failed to save record to storage file."

        return True, f"Student '{clean_name}' (ID: {clean_id}) added successfully."

    def update_student(
        self,
        student_id: str,
        name: Optional[str] = None,
        course: Optional[str] = None,
        marks: Optional[float] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Update existing student details."""
        target = self.get_student_by_id(student_id)
        if not target:
            return False, f"No student found with ID '{student_id}'."

        if name is not None and str(name).strip():
            if len(str(name).strip()) < 2:
                return False, "Student name must be at least 2 characters long."
            target.name = str(name).strip()

        if course is not None and str(course).strip():
            target.course = str(course).strip()

        if marks is not None:
            try:
                m = float(marks)
                if not 0.0 <= m <= 100.0:
                    return False, "Marks must be between 0.0 and 100.0."
                target.marks = m
            except (ValueError, TypeError):
                return False, "Invalid marks format."

        if email is not None:
            target.email = str(email).strip()

        if phone is not None:
            target.phone = str(phone).strip()

        saved = self.storage.save_students(self.students)
        if not saved:
            return False, "Failed to update record in storage."

        return True, f"Student '{student_id}' updated successfully."

    def delete_student(self, student_id: str) -> Tuple[bool, str]:
        """Delete student record by ID."""
        target = self.get_student_by_id(student_id)
        if not target:
            return False, f"No student found with ID '{student_id}'."

        self.students.remove(target)
        saved = self.storage.save_students(self.students)
        if not saved:
            return False, "Failed to update storage after deletion."

        return True, f"Student '{target.name}' (ID: {student_id}) deleted successfully."

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Lookup student by ID (case-insensitive)."""
        target_id = str(student_id).strip().upper()
        for s in self.students:
            if s.student_id.upper() == target_id:
                return s
        return None

    def get_all_students(self) -> List[Student]:
        """Return all student records."""
        return list(self.students)

    def get_unique_courses(self) -> List[str]:
        """Return sorted list of unique courses represented."""
        courses = {s.course for s in self.students if s.course}
        return sorted(list(courses))

    def search_and_filter(
        self,
        query: str = "",
        course_filter: str = "All",
        grade_filter: str = "All",
        status_filter: str = "All",
        sort_by: str = "id",
        reverse: bool = False,
    ) -> List[Student]:
        """Multi-criteria search, filter, and sort over student records."""
        q = query.strip().lower()
        results = []

        for s in self.students:
            # Query match across ID, Name, Course, Email, or Phone
            matches_query = (
                not q
                or q in s.student_id.lower()
                or q in s.name.lower()
                or q in s.course.lower()
                or q in s.email.lower()
                or q in s.phone.lower()
            )

            # Course match
            matches_course = (course_filter == "All" or s.course.lower() == course_filter.lower())

            # Grade match
            matches_grade = (grade_filter == "All" or s.get_grade() == grade_filter)

            # Status match
            matches_status = (status_filter == "All" or s.get_status().lower() == status_filter.lower())

            if matches_query and matches_course and matches_grade and matches_status:
                results.append(s)

        # Sorting
        if sort_by == "name":
            results.sort(key=lambda s: s.name.lower(), reverse=reverse)
        elif sort_by == "marks":
            results.sort(key=lambda s: s.marks, reverse=reverse)
        elif sort_by == "course":
            results.sort(key=lambda s: s.course.lower(), reverse=reverse)
        elif sort_by == "grade":
            results.sort(key=lambda s: s.get_grade(), reverse=reverse)
        else:  # default ID
            results.sort(key=lambda s: s.student_id.lower(), reverse=reverse)

        return results

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Compute key academic KPIs for the Dashboard page."""
        total = len(self.students)
        if total == 0:
            return {
                "total_students": 0,
                "average_marks": 0.0,
                "highest_marks": 0.0,
                "lowest_marks": 0.0,
                "passing_rate": 0.0,
                "grade_distribution": {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
                "status_distribution": {"Distinction": 0, "Passing": 0, "Needs Improvement": 0},
                "recent_students": [],
                "unique_courses": [],
            }

        all_marks = [s.marks for s in self.students]
        avg = sum(all_marks) / total
        highest = max(all_marks)
        lowest = min(all_marks)

        passing_count = sum(1 for m in all_marks if m >= 50.0)
        passing_rate = round((passing_count / total) * 100, 1)

        grade_dist = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        status_dist = {"Distinction": 0, "Passing": 0, "Needs Improvement": 0}

        for s in self.students:
            grade_dist[s.get_grade()] = grade_dist.get(s.get_grade(), 0) + 1
            status_dist[s.get_status()] = status_dist.get(s.get_status(), 0) + 1

        recent = list(reversed(self.students))[:5]

        return {
            "total_students": total,
            "average_marks": round(avg, 1),
            "highest_marks": round(highest, 1),
            "lowest_marks": round(lowest, 1),
            "passing_rate": passing_rate,
            "grade_distribution": grade_dist,
            "status_distribution": status_dist,
            "recent_students": recent,
            "unique_courses": self.get_unique_courses(),
        }

    def export_csv(self, filepath: Optional[str] = None) -> str:
        """Export all current students to CSV."""
        return self.storage.export_to_csv(self.students, filepath)
