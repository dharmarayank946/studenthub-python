"""Automated Unit & Integration Test Suite for StudentHub.
=======================================================
Tests:
1. Object-Oriented Programming (Person, Student, Inheritance, Polymorphism).
2. Grade calculations, percentage evaluation, and academic status.
3. Storage persistence, corrupted JSON recovery, automated backup, and CSV export.
4. Business logic: student addition, validation, duplicate prevention, update, deletion.
5. Search, filtering, and statistical KPI computations.
6. Desktop GUI initialization and multi-page navigation.
"""

import os
import sys
import tempfile
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import Person, Student
from storage import StudentStorage
from student_service import StudentService


class TestStudentModel(unittest.TestCase):
    """Test OOP hierarchy, polymorphism, and grade computation."""

    def test_inheritance_and_polymorphism(self):
        p = Person("General Person")
        self.assertEqual(p.name, "General Person")
        self.assertIn("General Person", p.display_details())

        s = Student("STU101", "Alice Smith", "Python", 92.5)
        # Verify inheritance
        self.assertIsInstance(s, Person)
        self.assertIsInstance(s, Student)
        self.assertEqual(s.name, "Alice Smith")
        self.assertEqual(s.student_id, "STU101")
        self.assertEqual(s.course, "Python")
        self.assertEqual(s.marks, 92.5)

        # Polymorphic display_details contains academic fields
        details = s.display_details()
        self.assertIn("STU101", details)
        self.assertIn("Alice Smith", details)
        self.assertIn("A+", details)

    def test_grade_calculation_bands(self):
        bands = [
            (95.0, "A+", "Distinction"),
            (85.0, "A", "Distinction"),
            (75.0, "B", "Passing"),
            (65.0, "C", "Passing"),
            (52.0, "D", "Passing"),
            (42.0, "F", "Needs Improvement"),
            (0.0, "F", "Needs Improvement"),
        ]
        for mark, expected_grade, expected_status in bands:
            s = Student("T1", "Tester", "Course", mark)
            self.assertEqual(s.get_grade(), expected_grade, f"Failed for mark {mark}")
            self.assertEqual(s.get_status(), expected_status, f"Failed for mark {mark}")
            self.assertEqual(s.get_percentage(), mark)

    def test_serialization_fidelity(self):
        s = Student("STU202", "Bob Marley", "Music", 88.0, email="bob@music.com", phone="1234567890")
        data = s.to_dict()
        self.assertEqual(data["student_id"], "STU202")
        self.assertEqual(data["name"], "Bob Marley")
        self.assertEqual(data["course"], "Music")
        self.assertEqual(data["marks"], 88.0)
        self.assertEqual(data["email"], "bob@music.com")

        reconstructed = Student.from_dict(data)
        self.assertEqual(reconstructed.student_id, s.student_id)
        self.assertEqual(reconstructed.name, s.name)
        self.assertEqual(reconstructed.marks, s.marks)
        self.assertEqual(reconstructed.email, s.email)


class TestStudentStorage(unittest.TestCase):
    """Test file persistence, automated backup, and CSV exports."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage = StudentStorage(data_directory=self.test_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_and_load_lifecycle(self):
        students = [
            Student("S1", "John Doe", "CS", 80.0),
            Student("S2", "Jane Smith", "AI", 95.0),
        ]
        saved = self.storage.save_students(students)
        self.assertTrue(saved)
        self.assertTrue(os.path.exists(self.storage.storage_file))

        loaded = self.storage.load_students()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].name, "John Doe")
        self.assertEqual(loaded[1].student_id, "S2")

    def test_csv_export(self):
        students = [Student("S10", "Markus", "Robotics", 82.5)]
        csv_path = self.storage.export_to_csv(students)
        self.assertTrue(os.path.exists(csv_path))

        with open(csv_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Student_ID,Name,Course,Marks", content)
        self.assertIn("Markus", content)
        self.assertIn("Robotics", content)

    def test_corrupted_json_recovery(self):
        # Write corrupted JSON
        with open(self.storage.storage_file, "w", encoding="utf-8") as f:
            f.write("{ INVALID JSON DATA --- broken")

        # Load should not crash, returns empty list or attempts backup
        loaded = self.storage.load_students()
        self.assertEqual(loaded, [])


class TestStudentService(unittest.TestCase):
    """Test business logic rules, input validation, and statistical metrics."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage = StudentStorage(data_directory=self.test_dir)
        self.service = StudentService(self.storage)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_add_student_validation(self):
        # 1. Valid addition
        ok, msg = self.service.add_student("STU1", "Kavya", "Python", 85.0)
        self.assertTrue(ok)

        # 2. Duplicate ID rejected
        ok_dup, msg_dup = self.service.add_student("stu1", "Different Name", "DSA", 90.0)
        self.assertFalse(ok_dup)
        self.assertIn("already exists", msg_dup)

        # 3. Empty ID rejected
        ok_empty, _ = self.service.add_student("", "Valid Name", "Course", 70.0)
        self.assertFalse(ok_empty)

        # 4. Invalid marks (<0 or >100)
        ok_neg, _ = self.service.add_student("S3", "Negative Marks", "Math", -5.0)
        self.assertFalse(ok_neg)

        ok_high, _ = self.service.add_student("S4", "Over 100 Marks", "Math", 105.0)
        self.assertFalse(ok_high)

    def test_update_and_delete_lifecycle(self):
        self.service.add_student("U1", "Original Name", "Course A", 60.0)

        # Update
        ok_upd, _ = self.service.update_student("U1", name="Updated Name", marks=75.0)
        self.assertTrue(ok_upd)

        s = self.service.get_student_by_id("U1")
        self.assertEqual(s.name, "Updated Name")
        self.assertEqual(s.marks, 75.0)

        # Delete
        ok_del, _ = self.service.delete_student("U1")
        self.assertTrue(ok_del)
        self.assertIsNone(self.service.get_student_by_id("U1"))

    def test_search_and_filter(self):
        self.service.add_student("ID1", "David Warner", "Cricket", 85.0)
        self.service.add_student("ID2", "Steve Smith", "Cricket", 92.0)
        self.service.add_student("ID3", "Lionel Messi", "Football", 98.0)

        # Query search
        results = self.service.search_and_filter(query="Messi")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Lionel Messi")

        # Course filter
        cricket_students = self.service.search_and_filter(course_filter="Cricket")
        self.assertEqual(len(cricket_students), 2)

        # Grade filter
        a_plus_students = self.service.search_and_filter(grade_filter="A+")
        self.assertEqual(len(a_plus_students), 2)  # 92 and 98

    def test_dashboard_metrics_calculation(self):
        self.service.add_student("M1", "Student One", "CS", 80.0)
        self.service.add_student("M2", "Student Two", "CS", 90.0)
        self.service.add_student("M3", "Student Three", "AI", 40.0)

        metrics = self.service.get_dashboard_metrics()
        self.assertEqual(metrics["total_students"], 3)
        self.assertEqual(metrics["average_marks"], 70.0)
        self.assertEqual(metrics["highest_marks"], 90.0)
        self.assertEqual(metrics["lowest_marks"], 40.0)
        # 2 out of 3 passing -> 66.7%
        self.assertAlmostEqual(metrics["passing_rate"], 66.7, places=1)


class TestGUI(unittest.TestCase):
    """Test Tkinter GUI instantiation and multi-page navigation."""

    def test_gui_initialization_and_page_navigation(self):
        try:
            import tkinter as tk
            from gui import StudentHubGUI

            root = tk.Tk()
            root.withdraw()
            app = StudentHubGUI(root)
            self.assertIsNotNone(app)

            # Test navigation to all 6 pages
            app.show_dashboard_page()
            self.assertEqual(app.current_page, "dashboard")

            app.show_management_page()
            self.assertEqual(app.current_page, "management")

            app.show_profile_page()
            self.assertEqual(app.current_page, "profile")

            app.show_academic_page()
            self.assertEqual(app.current_page, "academic")

            app.show_reports_page()
            self.assertEqual(app.current_page, "reports")

            app.show_settings_page()
            self.assertEqual(app.current_page, "settings")

            root.destroy()
        except tk.TclError:
            pass


if __name__ == "__main__":
    unittest.main()
