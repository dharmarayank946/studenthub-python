"""Student Management System.

Week 2 Python Development Internship:
- Data Structures: Lists, Tuples, Sets, Dictionaries
- Object-Oriented Programming: Classes, Objects, Constructors, Inheritance, Polymorphism
- File Storage: JSON persistence
- Exception Handling: Input validation and file operations
"""

import json
import os

# Menu options represented as an immutable tuple of (choice_key, description)
MENU_OPTIONS = (
    ("1", "Add Student"),
    ("2", "View All Students"),
    ("3", "Search Student by ID"),
    ("4", "Update Student Details"),
    ("5", "Delete Student Record"),
    ("6", "Exit"),
)


class Person:
    """Base class representing a person with a name.
    
    Demonstrates OOP Concept: Base Class & Inheritance.
    """

    def __init__(self, name: str):
        self.name = name.strip()

    def display_details(self):
        """Display details of a person.
        
        Demonstrates OOP Concept: Polymorphism (to be overridden by subclasses).
        """
        print(f"Name       : {self.name}")


class Student(Person):
    """Represent a student and their academic details.
    
    Demonstrates OOP Concepts:
    - Inheritance (inherits from Person)
    - Constructor chaining (super().__init__)
    - Polymorphism (overrides display_details)
    """

    def __init__(self, student_id: str, name: str, course: str, marks: float):
        super().__init__(name)
        self.student_id = student_id.strip()
        self.course = course.strip()
        self.marks = float(marks)

    def display_details(self):
        """Display student information, overriding Person.display_details (Polymorphism)."""
        print(f"Student ID : {self.student_id}")
        super().display_details()
        print(f"Course     : {self.course}")
        print(f"Marks      : {self.marks:.1f}")

    def to_dict(self):
        """Convert student object to a dictionary for JSON serialization."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "course": self.course,
            "marks": self.marks,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create a Student object from a dictionary."""
        return cls(
            student_id=data["student_id"],
            name=data["name"],
            course=data["course"],
            marks=data["marks"],
        )


class StudentManagementSystem:
    """Manage student records with JSON file persistence."""

    def __init__(self, storage_path: str = None):
        # Resolve the storage file path relative to this script's directory
        if storage_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.storage_file = os.path.join(base_dir, "students.json")
        else:
            self.storage_file = storage_path

        # List data structure to hold student records
        self.students = []
        self.load_students()

    def get_existing_ids(self) -> set:
        """Return a set of all existing student IDs for fast O(1) membership lookup.
        
        Demonstrates Data Structure: Sets.
        """
        return {student.student_id.upper() for student in self.students}

    def add_student(self):
        """Add a new student with validation for unique ID, non-empty fields, and valid marks."""
        print("\n--- Add New Student ---")
        student_id = input("Enter Student ID: ").strip()

        if not student_id:
            print("Error: Student ID cannot be empty.")
            return

        # Check for unique student ID using set lookup
        if student_id.upper() in self.get_existing_ids():
            print(f"Error: A student with ID '{student_id}' already exists.")
            return

        name = input("Enter Student Name: ").strip()
        if not name:
            print("Error: Student name cannot be empty.")
            return

        course = input("Enter Course: ").strip()
        if not course:
            print("Error: Course cannot be empty.")
            return

        # Exception handling for marks input
        try:
            marks_input = input("Enter Marks (0 - 100): ").strip()
            marks = float(marks_input)
            if not 0 <= marks <= 100:
                print("Error: Marks must be between 0 and 100.")
                return
        except ValueError:
            print("Error: Invalid marks. Please enter a valid numerical value.")
            return

        # Create and store the new Student object
        new_student = Student(student_id, name, course, marks)
        self.students.append(new_student)
        self.save_students()
        print(f"Success: Student '{name}' (ID: {student_id}) added successfully.")

    def view_students(self):
        """Display all student records formatted cleanly."""
        print("\n--- All Student Records ---")
        if not self.students:
            print("No student records found.")
            return

        print(f"Total Students: {len(self.students)}")
        print("=" * 36)
        for index, student in enumerate(self.students, start=1):
            print(f"Record #{index}")
            student.display_details()
            print("-" * 36)

    def search_student(self):
        """Search for a student by ID."""
        print("\n--- Search Student ---")
        student_id = input("Enter Student ID to search: ").strip()

        if not student_id:
            print("Error: Student ID cannot be empty.")
            return

        target_id = student_id.upper()
        for student in self.students:
            if student.student_id.upper() == target_id:
                print("\nStudent Record Found:")
                print("=" * 36)
                student.display_details()
                print("=" * 36)
                return

        print(f"No student found with ID '{student_id}'.")

    def update_student(self):
        """Update existing student details (name, course, marks)."""
        print("\n--- Update Student Details ---")
        student_id = input("Enter Student ID to update: ").strip()

        if not student_id:
            print("Error: Student ID cannot be empty.")
            return

        target_id = student_id.upper()
        target_student = None
        for student in self.students:
            if student.student_id.upper() == target_id:
                target_student = student
                break

        if not target_student:
            print(f"No student found with ID '{student_id}'.")
            return

        print("\nCurrent Details:")
        target_student.display_details()
        print("\n(Press Enter without typing to keep the current value)")

        # Update Name
        new_name = input(f"Enter New Name [{target_student.name}]: ").strip()
        if new_name:
            target_student.name = new_name

        # Update Course
        new_course = input(f"Enter New Course [{target_student.course}]: ").strip()
        if new_course:
            target_student.course = new_course

        # Update Marks
        new_marks_input = input(f"Enter New Marks [{target_student.marks}]: ").strip()
        if new_marks_input:
            try:
                new_marks = float(new_marks_input)
                if not 0 <= new_marks <= 100:
                    print("Error: Marks must be between 0 and 100. Update cancelled.")
                    return
                target_student.marks = new_marks
            except ValueError:
                print("Error: Invalid marks format. Update cancelled.")
                return

        self.save_students()
        print(f"Success: Student '{target_student.student_id}' updated successfully.")

    def delete_student(self):
        """Delete a student record by ID."""
        print("\n--- Delete Student Record ---")
        student_id = input("Enter Student ID to delete: ").strip()

        if not student_id:
            print("Error: Student ID cannot be empty.")
            return

        target_id = student_id.upper()
        for student in self.students:
            if student.student_id.upper() == target_id:
                confirm = input(f"Are you sure you want to delete '{student.name}' (ID: {student.student_id})? (y/n): ").strip().lower()
                if confirm == "y":
                    self.students.remove(student)
                    self.save_students()
                    print(f"Success: Student record '{student.student_id}' deleted successfully.")
                else:
                    print("Deletion cancelled.")
                return

        print(f"No student found with ID '{student_id}'.")

    def save_students(self):
        """Serialize student objects to dictionaries and save to JSON file."""
        data = [student.to_dict() for student in self.students]
        try:
            with open(self.storage_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except OSError as error:
            print(f"Error: Unable to save records to file ({error}).")

    def load_students(self):
        """Load student records from the JSON file into Student objects."""
        if not os.path.exists(self.storage_file):
            self.students = []
            return

        try:
            with open(self.storage_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                print("Warning: Storage file does not contain a valid list of students.")
                self.students = []
                return

            self.students = []
            for item in data:
                try:
                    student = Student.from_dict(item)
                    self.students.append(student)
                except (KeyError, TypeError, ValueError) as item_error:
                    print(f"Warning: Skipping corrupted record: {item_error}")

        except json.JSONDecodeError:
            print("Warning: File contains invalid JSON format. Starting with an empty list.")
            self.students = []
        except OSError as error:
            print(f"Error: Unable to read storage file ({error}).")
            self.students = []


def display_menu():
    """Display the interactive menu options."""
    print("\n" + "=" * 36)
    print("     STUDENT MANAGEMENT SYSTEM")
    print("=" * 36)
    for key, label in MENU_OPTIONS:
        print(f"  {key}. {label}")
    print("=" * 36)


def main():
    """Main program execution loop."""
    system = StudentManagementSystem()

    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            system.add_student()
        elif choice == "2":
            system.view_students()
        elif choice == "3":
            system.search_student()
        elif choice == "4":
            system.update_student()
        elif choice == "5":
            system.delete_student()
        elif choice == "6":
            print("\nExiting Student Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please select an option between 1 and 6.")


if __name__ == "__main__":
    main()
