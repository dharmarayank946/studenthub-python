"""StudentHub — Data Models.
===========================
Demonstrates Week 2 Object-Oriented Programming (OOP) requirements:
- Base class: Person (encapsulating person attributes)
- Inheritance: Student inherits from Person
- Constructor chaining: super().__init__()
- Polymorphism: display_details() override
- Encapsulation: getters, grade calculations, validation, serialization
"""

from typing import Dict, Any, Optional


class Person:
    """Base class representing a person.
    
    Demonstrates OOP Concept: Base Class & Inheritance.
    """

    def __init__(self, name: str):
        self.name = name.strip()

    def display_details(self) -> str:
        """Display details of a person (to be overridden by subclasses)."""
        return f"Name: {self.name}"

    def __repr__(self) -> str:
        return f"<Person name='{self.name}'>"


class Student(Person):
    """Represents a student entity with academic metrics.
    
    Demonstrates OOP Concepts:
    - Inheritance (inherits from Person)
    - Constructor chaining (super().__init__)
    - Polymorphism (overrides display_details)
    - Encapsulation & computed properties (grade, status, percentage)
    """

    def __init__(
        self,
        student_id: str,
        name: str,
        course: str,
        marks: float,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        enrollment_date: Optional[str] = None,
    ):
        super().__init__(name)
        self.student_id = str(student_id).strip()
        self.course = str(course).strip()
        self.marks = float(marks)
        self.email = str(email).strip() if email else ""
        self.phone = str(phone).strip() if phone else ""
        self.enrollment_date = str(enrollment_date).strip() if enrollment_date else ""

    def get_percentage(self) -> float:
        """Calculate and return marks percentage (standard 0-100 scale)."""
        return round(self.marks, 1)

    def get_grade(self) -> str:
        """Calculate academic grade letter based on standard university bands."""
        m = self.marks
        if m >= 90:
            return "A+"
        if m >= 80:
            return "A"
        if m >= 70:
            return "B"
        if m >= 60:
            return "C"
        if m >= 50:
            return "D"
        return "F"

    def get_status(self) -> str:
        """Determine academic standing status."""
        m = self.marks
        if m >= 85:
            return "Distinction"
        if m >= 50:
            return "Passing"
        return "Needs Improvement"

    def display_details(self) -> str:
        """Display formatted student details, overriding Person.display_details (Polymorphism)."""
        return (
            f"Student ID : {self.student_id}\n"
            f"Name       : {self.name}\n"
            f"Course     : {self.course}\n"
            f"Marks      : {self.marks:.1f}\n"
            f"Grade      : {self.get_grade()}\n"
            f"Status     : {self.get_status()}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert student object to dictionary for clean JSON serialization.
        
        Preserves backward compatibility with original Week 2 schema.
        """
        data = {
            "student_id": self.student_id,
            "name": self.name,
            "course": self.course,
            "marks": self.marks,
        }
        if self.email:
            data["email"] = self.email
        if self.phone:
            data["phone"] = self.phone
        if self.enrollment_date:
            data["enrollment_date"] = self.enrollment_date
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        """Instantiate a Student object from a dictionary with safe defaults."""
        return cls(
            student_id=data.get("student_id", ""),
            name=data.get("name", "Unknown"),
            course=data.get("course", "General"),
            marks=float(data.get("marks", 0.0)),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            enrollment_date=data.get("enrollment_date", ""),
        )

    def __repr__(self) -> str:
        return f"<Student id='{self.student_id}' name='{self.name}' marks={self.marks}>"
