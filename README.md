# StudentHub — Professional Student Management System

> **Internship:** Python Development Internship — Week 2 Project Upgrade  
> **Core Focus:** Object-Oriented Programming (OOP), Data Structures, JSON File Persistence, Data Validation, CSV Reporting, and Multi-Page Tkinter Desktop GUI.

---

## 1. Project Overview

**StudentHub** is an upgraded desktop application built for **Week 2 of the Python Development Internship**. It elevates the initial terminal script into a modern multi-page desktop experience inspired by **QuizUp Python Edition** and **WeatherWise V3**.

It preserves the foundational Python OOP principles (`Person` base class, `Student` inheritance, constructor chaining, and polymorphism) while adding a Tkinter interface with academic analytics, search and filtering, individual profile cards, and automated data backups.

---

## 2. Features

### V3 Professional Multi-Page Desktop GUI
The graphical interface is built entirely with Python standard library `tkinter`:

1. **📊 Dashboard:**
   - Real-time KPI summary cards: Total Enrolled Students, Class Average Marks, Passing Rate (%), and Distinctions count.
   - Interactive Grade Distribution Bar Chart drawn on native `tk.Canvas` with color-coded grade bands (`A+`, `A`, `B`, `C`, `D`, `F`).
   - Recently enrolled students table with one-click profile inspection.
   - Quick action launchers for record creation and CSV generation.

2. **👥 Student Management:**
   - Multi-field search box (matches by ID, Name, Course, or Email in real-time).
   - Filter dropdowns by Enrolled Course and Grade Letter.
   - Sortable `ttk.Treeview` table displaying student records with status pills.
   - Interactive Modal Forms for adding and editing records with input validation.
   - Confirmation dialog before record deletion to prevent accidental data loss.

3. **👤 Student Profile:**
   - Dropdown selector for rapid student lookup.
   - Profile Hero Card featuring student avatar initials, ID, Course, and Academic Standing (`Distinction`, `Passing`, `Needs Improvement`).
   - Academic breakdown cards displaying percentage, awarded grade, and standing.
   - Contact and enrollment card displaying email, phone, and registration date.

4. **📈 Academic Performance:**
   - Cohort Statistical Summary: Class average, highest marks, lowest marks, and overall passing rate.
   - Academic Honor Roll ranking top performers across all courses.
   - Grade and academic tier breakdown.

5. **📑 Reports & Export:**
   - In-app storage diagnostics showing database file path, file size, record count, and backup status.
   - One-click **Export to CSV** creating standardized `.csv` spreadsheets in the `reports/` directory with file-save dialog support.

6. **⚙️ Preferences & Settings:**
   - Visual Theme presets (*Sky Blue*, *Soft Lavender*, *Slate*).
   - Academic grading reference scale guide.
   - Automated safety backup status (`students_backup.json`).

---

## 3. Mapping of Week 2 Python Requirements

| Requirement | Implementation File | Component / Function | Description |
| :--- | :--- | :--- | :--- |
| **Classes & Objects** | [`models.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/models.py) | `Person`, `Student` | Models student entities, encapsulating properties and grade calculations. |
| **Inheritance** | [`models.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/models.py) | `class Student(Person)` | Inherits person attributes (`name`) from `Person` base class. |
| **Constructor Chaining** | [`models.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/models.py) | `super().__init__(name)` | Chains subclass constructor to base class initialization. |
| **Polymorphism** | [`models.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/models.py) | `display_details()` | Overrides base class method to display academic metrics and grades. |
| **Lists** | [`student_service.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/student_service.py) | `self.students` | Manages ordered collection of active student records. |
| **Tuples** | [`student_management.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/student_management.py) | `MENU_OPTIONS` | Stores immutable tuple of menu keys and descriptive labels. |
| **Sets** | [`student_service.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/student_service.py) | `get_existing_ids()` | Generates a set of student IDs for $O(1)$ fast duplicate prevention. |
| **Dictionaries** | [`models.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/models.py) | `to_dict()` & `from_dict()` | Maps between Python `Student` objects and JSON dictionary payloads. |
| **JSON File Persistence** | [`storage.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/storage.py) | `StudentStorage.save_students()` | Serializes records to `students.json` with automatic backup creation. |
| **Exception Handling** | [`storage.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/storage.py) & [`student_service.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/student_service.py) | `try...except` | Catches `JSONDecodeError`, `OSError`, `ValueError`, and handles corrupted files. |
| **Original Terminal Menu** | [`student_management.py`](file:///d:/Projects/Python%20Internship/Student%20Management%20System/student_management.py) | `main()` | Preserves the original 6-option interactive terminal menu. |

---

## 4. Project Structure

```text
Student Management System/
├── main.py                       # Unified entry point (Default: Launches GUI)
├── gui.py                        # StudentHub 6-page Tkinter desktop interface
├── models.py                     # Person base class, Student subclass, grade logic
├── storage.py                    # JSON persistence, automatic backups, CSV exporter
├── student_service.py            # Business logic, validation, search, filter, KPIs
├── student_management.py         # Original Week 2 OOP classes and terminal CLI
├── student_management_backup.py  # Safety backup of original student_management.py
├── students.json                 # Primary persistent JSON storage
├── students_backup.json          # Automated safety backup
├── README.md                     # Project documentation and guide
├── reports/                      # Auto-generated CSV export spreadsheets
└── tests/
    └── test_student_hub.py      # Automated unit and integration test suite
```

---

## 5. How to Run

### Method 1: Desktop Graphical Application (Default)
```powershell
python main.py
```
*(Or run `python gui.py` directly).*

### Method 2: Original Terminal Application
To run the interactive menu in the terminal:
```powershell
python main.py --cli
```
*(Or run `python student_management.py` directly).*

```text
====================================
     STUDENT MANAGEMENT SYSTEM
====================================
  1. Add Student
  2. View All Students
  3. Search Student by ID
  4. Update Student Details
  5. Delete Student Record
  6. Exit
====================================
```

### Method 3: Automated Test Suite
```powershell
python main.py --test
```
*(Or run `python -m unittest discover tests`).*

---

## 6. Automated Test Results

```text
test_gui_initialization_and_page_navigation (test_student_hub.TestGUI) ... ok
test_grade_calculation_bands (test_student_hub.TestStudentModel) ... ok
test_inheritance_and_polymorphism (test_student_hub.TestStudentModel) ... ok
test_serialization_fidelity (test_student_hub.TestStudentModel) ... ok
test_add_student_validation (test_student_hub.TestStudentService) ... ok
test_dashboard_metrics_calculation (test_student_hub.TestStudentService) ... ok
test_search_and_filter (test_student_hub.TestStudentService) ... ok
test_update_and_delete_lifecycle (test_student_hub.TestStudentService) ... ok
test_corrupted_json_recovery (test_student_hub.TestStudentStorage) ... ok
test_csv_export (test_student_hub.TestStudentStorage) ... ok
test_save_and_load_lifecycle (test_student_hub.TestStudentStorage) ... ok

----------------------------------------------------------------------
Ran 11 tests in 2.352s

OK
```

All 11 unit and integration tests passed (100% success rate).

---

## 7. Safety & Isolation Notice
- **Week 1** ([`Basic Calculator`](file:///d:/Projects/Python%20Internship/Basic%20Calculator)), **Week 3** ([`Weather App`](file:///d:/Projects/Python%20Internship/Weather%20App)), and **Week 4** ([`QuizUp Python Edition`](file:///d:/Projects/Python%20Internship/QuizUp%20Python%20Edition)) remain completely untouched.
- Existing student records (`Ananya`, `nidhi`) in `students.json` were preserved.
- All changes are local; nothing has been pushed to GitHub.
