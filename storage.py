"""StudentHub — Storage Engine.
==============================
Handles JSON file persistence, automated data backups, recovery from
corrupted files, CSV exports, and user settings.
"""

import csv
import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional

from models import Student


class StudentStorage:
    """Manages persistent JSON storage and CSV exports for StudentHub."""

    def __init__(self, data_directory: Optional[str] = None):
        if data_directory is None:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.base_dir = data_directory

        self.storage_file = os.path.join(self.base_dir, "students.json")
        self.backup_file = os.path.join(self.base_dir, "students_backup.json")
        self.settings_file = os.path.join(self.base_dir, "settings.json")
        self.reports_dir = os.path.join(self.base_dir, "reports")

        os.makedirs(self.reports_dir, exist_ok=True)

    def load_students(self) -> List[Student]:
        """Load student records from students.json into Student objects.
        
        Recovers gracefully from missing, empty, or corrupted files.
        """
        if not os.path.exists(self.storage_file):
            return []

        if os.path.getsize(self.storage_file) == 0:
            return []

        try:
            with open(self.storage_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                print("[Warning] Storage file format is invalid (not a list). Returning empty list.")
                return []

            students = []
            for item in data:
                if isinstance(item, dict) and "student_id" in item:
                    try:
                        student = Student.from_dict(item)
                        students.append(student)
                    except (ValueError, TypeError) as parse_error:
                        print(f"[Warning] Skipping corrupted student record: {parse_error}")

            return students

        except json.JSONDecodeError as json_error:
            print(f"[Warning] JSON decode error in {self.storage_file}: {json_error}. Attempting backup recovery...")
            return self._attempt_backup_recovery()
        except OSError as os_error:
            print(f"[Error] OS error reading {self.storage_file}: {os_error}")
            return []

    def save_students(self, students: List[Student]) -> bool:
        """Serialize student objects to dictionaries and save to students.json.
        
        Creates a safety backup before overwriting.
        """
        # Create safety backup if file exists and has content
        if os.path.exists(self.storage_file) and os.path.getsize(self.storage_file) > 0:
            try:
                shutil.copy2(self.storage_file, self.backup_file)
            except OSError:
                pass

        data = [student.to_dict() for student in students]

        try:
            with open(self.storage_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            return True
        except OSError as error:
            print(f"[Error] Failed to save students to {self.storage_file}: {error}")
            return False

    def _attempt_backup_recovery(self) -> List[Student]:
        """Attempt to recover students from backup if primary file is corrupted."""
        if not os.path.exists(self.backup_file):
            return []

        try:
            with open(self.backup_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, list):
                print("[Info] Successfully recovered records from backup file.")
                return [Student.from_dict(item) for item in data if isinstance(item, dict)]
        except Exception:
            pass

        return []

    def export_to_csv(self, students: List[Student], filepath: Optional[str] = None) -> str:
        """Export all student records to a clean CSV report file."""
        if filepath is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_path = os.path.join(self.reports_dir, f"student_report_{ts}.csv")
        else:
            target_path = filepath

        headers = [
            "Student_ID",
            "Name",
            "Course",
            "Marks",
            "Percentage",
            "Grade",
            "Status",
            "Email",
            "Phone",
            "Enrollment_Date",
        ]

        try:
            with open(target_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                for s in students:
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
                        s.enrollment_date,
                    ])
            return target_path
        except OSError as error:
            print(f"[Error] Failed to export CSV: {error}")
            return ""

    def get_settings(self) -> Dict[str, Any]:
        """Load user display preferences from settings.json."""
        defaults = {
            "theme": "Sky Blue",
            "default_course": "Python",
            "auto_save": True,
            "table_rows_per_page": 20,
        }

        if not os.path.exists(self.settings_file):
            return defaults

        try:
            with open(self.settings_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    defaults.update(data)
                    return defaults
        except Exception:
            pass

        return defaults

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save user preferences to settings.json."""
        curr = self.get_settings()
        curr.update(settings)
        try:
            with open(self.settings_file, "w", encoding="utf-8") as file:
                json.dump(curr, file, indent=4)
            return True
        except OSError:
            return False

    def get_storage_stats(self) -> Dict[str, Any]:
        """Return diagnostic metrics about storage."""
        size_bytes = os.path.getsize(self.storage_file) if os.path.exists(self.storage_file) else 0
        backup_exists = os.path.exists(self.backup_file)
        return {
            "storage_file": self.storage_file,
            "size_bytes": size_bytes,
            "backup_exists": backup_exists,
        }
