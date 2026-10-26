"""StudentHub — Enterprise Academic Portal (Vertical Sidebar Edition).
===================================================================
A professional enterprise desktop application featuring a deep navy
vertical left sidebar, breadcrumb navigation, and emerald academic styling.

Navigation & Layout:
- Left Vertical Sidebar (220px): Deep Navy (#0F172A) with stacked vertical navigation items:
  1. 📊 Dashboard
  2. 👥 Student Directory
  3. 👤 Student Profile
  4. 📈 Academic Performance
  5. 📑 Reports & Export
  6. ⚙️ System Settings
- Top Breadcrumb & Status Header on the right: Breadcrumb trail, global search, and KPI badges.
- Content Canvas: Data-dense, clean academic cards with Emerald Green (#059669) & Amber (#D97706) accents.
"""

import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from models import Student
from storage import StudentStorage
from student_service import StudentService


# =============================================================================
# Academic Emerald & Deep Navy Palette
# =============================================================================
COLOR_SIDEBAR_BG = "#0F172A"       # Deep Enterprise Navy Sidebar
COLOR_SIDEBAR_HOVER = "#1E293B"    # Sidebar link hover
COLOR_SIDEBAR_ACTIVE = "#059669"   # Active menu item: Vivid Academic Emerald
COLOR_SIDEBAR_TEXT = "#94A3B8"     # Muted text on navy
COLOR_SIDEBAR_ACTIVE_TEXT = "#FFFFFF"

COLOR_CANVAS_BG = "#F8FAFC"        # Crisp warm ivory / soft slate main canvas
COLOR_CARD_BG = "#FFFFFF"          # Pure white elevated card surfaces
COLOR_CARD_SUB = "#F1F5F9"         # Subtle container background
COLOR_BORDER = "#E2E8F0"           # Light perimeter border

COLOR_PRIMARY = "#059669"          # Emerald Green (Primary Academic Accent)
COLOR_PRIMARY_HOVER = "#047857"
COLOR_ACCENT = "#0284C7"           # Secondary Ocean Blue
COLOR_AMBER = "#D97706"            # Warm Amber Gold for Distinctions & Awards

COLOR_TEXT_MAIN = "#0F172A"        # High-contrast deep slate text
COLOR_TEXT_MUTED = "#64748B"       # Secondary text

COLOR_BADGE_BG = "#ECFDF5"         # Soft emerald badge
COLOR_BADGE_FG = "#065F46"
COLOR_DANGER_BG = "#FEE2E2"        # Danger red
COLOR_DANGER_FG = "#B91C1C"


class StudentHubGUI:
    """Enterprise Academic Desktop Application with Left Sidebar."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("StudentHub ✦ Enterprise Academic Portal")
        self.root.geometry("1160x820")
        self.root.minsize(980, 700)
        self.root.configure(bg=COLOR_CANVAS_BG)

        # Center and elevate window in front of VS Code / terminal on startup
        self._center_and_elevate_window(1140, 740)

        # Backend service & storage
        self.storage = StudentStorage()
        self.service = StudentService(self.storage)

        # State
        self.current_page = "dashboard"
        self.nav_buttons = {}
        self.selected_student_for_profile = None

        # Build Main Frame: Left Sidebar + Right Content Area
        self._build_sidebar_and_content_split()

        # Start on Dashboard
        self.show_dashboard_page()

    def _center_and_elevate_window(self, width: int, height: int):
        """Center window on screen and elevate smoothly in front of all applications."""
        try:
            self.root.update_idletasks()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            w = min(width, sw - 40)
            h = min(height, sh - 80)
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2)
            self.root.geometry(f"{w}x{h}+{x}+{y}")
            self.root.minsize(940, 620)
            self.root.deiconify()
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.after(800, lambda: self.root.attributes("-topmost", False))
            self.root.focus_force()
        except Exception:
            pass

    # =========================================================================
    # Two-Column Layout: Left Vertical Sidebar + Right Content Area
    # =========================================================================
    def _build_sidebar_and_content_split(self):
        """Construct the enterprise left vertical sidebar and right workspace."""
        self.app_frame = tk.Frame(self.root, bg=COLOR_CANVAS_BG)
        self.app_frame.pack(fill=tk.BOTH, expand=True)

        # ---------------- 1. Left Vertical Sidebar (220px) ----------------
        self.sidebar = tk.Frame(self.app_frame, bg=COLOR_SIDEBAR_BG, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Sidebar Header: Branding
        sb_brand = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR_BG, padx=16, pady=20)
        sb_brand.pack(fill=tk.X)

        tk.Label(
            sb_brand,
            text="🎓 StudentHub",
            font=("Segoe UI", 15, "bold"),
            fg="#FFFFFF",
            bg=COLOR_SIDEBAR_BG
        ).pack(anchor="w")

        tk.Label(
            sb_brand,
            text="Academic Portal • Week 2",
            font=("Segoe UI", 8),
            fg="#38BDF8",
            bg=COLOR_SIDEBAR_BG
        ).pack(anchor="w", pady=(2, 0))

        # Thin separator line
        tk.Frame(self.sidebar, bg="#1E293B", height=1).pack(fill=tk.X, padx=12, pady=(0, 16))

        # Vertical Navigation Items
        self.nav_menu_frame = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR_BG)
        self.nav_menu_frame.pack(fill=tk.X, padx=10)

        nav_items = [
            ("dashboard", "📊  Dashboard", self.show_dashboard_page),
            ("management", "👥  Directory", self.show_management_page),
            ("profile", "👤  Student Profile", self.show_profile_page),
            ("academic", "📈  Performance", self.show_academic_page),
            ("reports", "📑  Export & Reports", self.show_reports_page),
            ("settings", "⚙️  Settings", self.show_settings_page),
        ]

        self.nav_buttons = {}
        for key, label, cmd in nav_items:
            btn = tk.Button(
                self.nav_menu_frame,
                text=label,
                font=("Segoe UI", 10, "bold"),
                bg=COLOR_SIDEBAR_BG,
                fg=COLOR_SIDEBAR_TEXT,
                activebackground=COLOR_SIDEBAR_HOVER,
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                anchor="w",
                padx=14,
                pady=10,
                cursor="hand2",
                bd=0,
                command=cmd
            )
            btn.pack(fill=tk.X, pady=3)
            self.nav_buttons[key] = btn

        # Sidebar Bottom Footer: Quick Action & Storage Badge
        sb_footer = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR_BG, padx=14, pady=16)
        sb_footer.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(
            sb_footer,
            text="➕ New Student",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_PRIMARY,
            fg="#FFFFFF",
            activebackground=COLOR_PRIMARY_HOVER,
            relief=tk.FLAT,
            padx=12,
            pady=8,
            cursor="hand2",
            bd=0,
            command=self.open_add_student_modal
        ).pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            sb_footer,
            text="Enterprise Storage: JSON\nAuto-Backups Active",
            font=("Segoe UI", 7),
            fg="#64748B",
            bg=COLOR_SIDEBAR_BG,
            justify=tk.CENTER
        ).pack(fill=tk.X)

        # ---------------- 2. Right Main Workspace Area ----------------
        self.main_workspace = tk.Frame(self.app_frame, bg=COLOR_CANVAS_BG)
        self.main_workspace.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Top Breadcrumb & Status Header
        self._build_top_workspace_header()

        # Dynamic Content Container
        self.content_container = tk.Frame(self.main_workspace, bg=COLOR_CANVAS_BG)
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 16))

    def _build_top_workspace_header(self):
        """Construct top header in the workspace with breadcrumb and badges."""
        top_bar = tk.Frame(self.main_workspace, bg=COLOR_CANVAS_BG, height=54, padx=24, pady=12)
        top_bar.pack(fill=tk.X)

        # Left: Breadcrumb Trail
        self.breadcrumb_label = tk.Label(
            top_bar,
            text="StudentHub  /  Dashboard",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_TEXT_MAIN,
            bg=COLOR_CANVAS_BG
        )
        self.breadcrumb_label.pack(side=tk.LEFT)

        # Right: Live KPI Badges
        right_box = tk.Frame(top_bar, bg=COLOR_CANVAS_BG)
        right_box.pack(side=tk.RIGHT)

        metrics = self.service.get_dashboard_metrics()

        self.kpi_count_badge = tk.Label(
            right_box,
            text=f"👥 {metrics['total_students']} Students",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_BADGE_FG,
            bg=COLOR_BADGE_BG,
            padx=10,
            pady=3
        )
        self.kpi_count_badge.pack(side=tk.LEFT, padx=(0, 8))

        self.kpi_avg_badge = tk.Label(
            right_box,
            text=f"📈 Cohort Avg: {metrics['average_marks']}%",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_ACCENT,
            bg="#E0F2FE",
            padx=10,
            pady=3
        )
        self.kpi_avg_badge.pack(side=tk.LEFT)

    def _update_nav_highlight(self, active_key: str):
        """Update active link in the vertical sidebar and breadcrumb."""
        self.current_page = active_key
        key_names = {
            "dashboard": "Dashboard",
            "management": "Student Directory",
            "profile": "Student Profile",
            "academic": "Academic Performance",
            "reports": "Reports & Export",
            "settings": "System Settings",
        }
        self.breadcrumb_label.configure(text=f"StudentHub  /  {key_names.get(active_key, 'Portal')}")

        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(
                    bg=COLOR_SIDEBAR_ACTIVE,
                    fg=COLOR_SIDEBAR_ACTIVE_TEXT,
                    activebackground=COLOR_PRIMARY_HOVER,
                    activeforeground="#FFFFFF"
                )
            else:
                btn.configure(
                    bg=COLOR_SIDEBAR_BG,
                    fg=COLOR_SIDEBAR_TEXT,
                    activebackground=COLOR_SIDEBAR_HOVER,
                    activeforeground="#FFFFFF"
                )

        # Refresh badges
        m = self.service.get_dashboard_metrics()
        self.kpi_count_badge.configure(text=f"👥 {m['total_students']} Students")
        self.kpi_avg_badge.configure(text=f"📈 Cohort Avg: {m['average_marks']}%")

    def _clear_content(self):
        """Clear dynamic content workspace."""
        for widget in self.content_container.winfo_children():
            widget.destroy()

    def _create_scrollable_container(self) -> tk.Frame:
        """Create responsive scrollable workspace."""
        canvas = tk.Canvas(self.content_container, bg=COLOR_CANVAS_BG, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self.content_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_CANVAS_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_canvas_configure(event):
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            delta = -1 if event.delta < 0 else 1
            canvas.yview_scroll(delta * -1, "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        return scrollable_frame

    # =========================================================================
    # Page 1: Dashboard
    # =========================================================================
    def show_dashboard_page(self):
        """Render Dashboard page."""
        self._update_nav_highlight("dashboard")
        self._clear_content()

        container = self._create_scrollable_container()
        metrics = self.service.get_dashboard_metrics()

        # ---------------- Row 1: KPI Metric Cards ----------------
        kpi_row = tk.Frame(container, bg=COLOR_CANVAS_BG)
        kpi_row.pack(fill=tk.X, pady=(0, 16))

        cards_data = [
            ("👥 Enrolled Students", str(metrics["total_students"]), "Active student profiles", COLOR_PRIMARY),
            ("📈 Cohort Average", f"{metrics['average_marks']}%", f"Range: {metrics['lowest_marks']}% – {metrics['highest_marks']}%", COLOR_ACCENT),
            ("🎯 Passing Rate", f"{metrics['passing_rate']}%", "Marks >= 50.0%", COLOR_PRIMARY),
            ("🏆 Academic Honors", str(metrics["status_distribution"].get("Distinction", 0)), "Marks >= 85.0%", COLOR_AMBER),
        ]

        for i, (ctitle, cval, csub, color) in enumerate(cards_data):
            card = tk.Frame(
                kpi_row,
                bg=COLOR_CARD_BG,
                highlightbackground=COLOR_BORDER,
                highlightthickness=1,
                padx=18,
                pady=16
            )
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if i == 0 else 12, 0))

            tk.Label(card, text=ctitle, font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w")
            tk.Label(card, text=cval, font=("Segoe UI", 24, "bold"), fg=color, bg=COLOR_CARD_BG).pack(anchor="w", pady=(6, 2))
            tk.Label(card, text=csub, font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w")

        # ---------------- Row 2: Grade Distribution Canvas & Quick Actions ----------------
        mid_row = tk.Frame(container, bg=COLOR_CANVAS_BG)
        mid_row.pack(fill=tk.X, pady=(0, 16))

        # Grade Distribution Canvas
        chart_card = tk.Frame(
            mid_row,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=20,
            pady=16
        )
        chart_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        tk.Label(
            chart_card,
            text="📊 Cohort Grade Distribution",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_TEXT_MAIN,
            bg=COLOR_CARD_BG
        ).pack(anchor="w", pady=(0, 10))

        self._draw_grade_chart(chart_card, metrics["grade_distribution"], metrics["total_students"])

        # Quick Actions Card
        act_card = tk.Frame(
            mid_row,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=20,
            pady=16,
            width=280
        )
        act_card.pack(side=tk.RIGHT, fill=tk.BOTH)

        tk.Label(
            act_card,
            text="⚡ Management Actions",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_TEXT_MAIN,
            bg=COLOR_CARD_BG
        ).pack(anchor="w", pady=(0, 12))

        actions = [
            ("➕ Add Student Record", self.open_add_student_modal, COLOR_PRIMARY, "#FFFFFF"),
            ("👥 View Student Directory", self.show_management_page, "#E0F2FE", COLOR_ACCENT),
            ("📥 Export Directory to CSV", self._quick_export_csv, COLOR_CARD_SUB, COLOR_TEXT_MAIN),
            ("📈 Performance Rankings", self.show_academic_page, COLOR_CARD_SUB, COLOR_TEXT_MAIN),
        ]

        for text, cmd, bg_col, fg_col in actions:
            tk.Button(
                act_card,
                text=text,
                font=("Segoe UI", 9, "bold"),
                bg=bg_col,
                fg=fg_col,
                relief=tk.FLAT,
                padx=12,
                pady=7,
                cursor="hand2",
                bd=0,
                command=cmd
            ).pack(fill=tk.X, pady=(0, 8))

        # ---------------- Row 3: Recently Added Students ----------------
        rec_card = tk.Frame(
            container,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=20,
            pady=16
        )
        rec_card.pack(fill=tk.X)

        r_top = tk.Frame(rec_card, bg=COLOR_CARD_BG)
        r_top.pack(fill=tk.X, pady=(0, 10))

        tk.Label(r_top, text="🕒 Recently Enrolled Students", font=("Segoe UI", 12, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(side=tk.LEFT)

        tk.Button(
            r_top,
            text="All Records ➔",
            font=("Segoe UI", 9, "bold"),
            bg="#ECFDF5",
            fg=COLOR_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2",
            bd=0,
            command=self.show_management_page
        ).pack(side=tk.RIGHT)

        if not metrics["recent_students"]:
            tk.Label(rec_card, text="No student records found.", font=("Segoe UI", 9, "italic"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w", pady=10)
        else:
            for s in metrics["recent_students"]:
                row = tk.Frame(rec_card, bg=COLOR_CARD_SUB, padx=14, pady=8)
                row.pack(fill=tk.X, pady=(0, 4))

                tk.Label(row, text=f"🎓 {s.student_id}", font=("Segoe UI", 9, "bold"), fg=COLOR_PRIMARY, bg=COLOR_CARD_SUB, width=12, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=s.name, font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_SUB, width=22, anchor="w").pack(side=tk.LEFT, padx=10)
                tk.Label(row, text=s.course, font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_SUB, width=16, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=f"{s.marks:.1f}% ({s.get_grade()})", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_SUB, width=14, anchor="w").pack(side=tk.LEFT)

                tk.Button(
                    row,
                    text="Inspect Profile",
                    font=("Segoe UI", 8, "bold"),
                    bg="#ECFDF5",
                    fg=COLOR_PRIMARY,
                    relief=tk.FLAT,
                    padx=8,
                    pady=2,
                    cursor="hand2",
                    bd=0,
                    command=lambda stud=s: self._goto_profile(stud)
                ).pack(side=tk.RIGHT)

    def _draw_grade_chart(self, parent: tk.Frame, grade_dist: dict, total: int):
        """Draw grade distribution bars on native Canvas."""
        c_width = 460
        c_height = 160
        canvas = tk.Canvas(parent, width=c_width, height=c_height, bg=COLOR_CARD_BG, highlightthickness=0, bd=0)
        canvas.pack(fill=tk.X, expand=True)

        grades = ["A+", "A", "B", "C", "D", "F"]
        counts = [grade_dist.get(g, 0) for g in grades]
        max_c = max(max(counts), 1)

        pad_left = 30
        pad_bottom = 25
        usable_w = c_width - pad_left - 20
        usable_h = c_height - pad_bottom - 20
        bar_w = usable_w / len(grades)

        palette = {
            "A+": "#059669",
            "A": "#10B981",
            "B": "#0284C7",
            "C": "#D97706",
            "D": "#F59E0B",
            "F": "#DC2626",
        }

        for i, g in enumerate(grades):
            c = counts[i]
            x0 = pad_left + (i * bar_w) + 12
            x1 = x0 + bar_w - 24
            bar_h = (c / max_c) * usable_h if max_c > 0 else 0
            y1 = c_height - pad_bottom
            y0 = y1 - bar_h

            canvas.create_rectangle(x0, y0, x1, y1, fill=palette.get(g, COLOR_PRIMARY), outline="")

            if c > 0:
                canvas.create_text((x0 + x1) / 2, y0 - 8, text=str(c), font=("Segoe UI", 8, "bold"), fill=COLOR_TEXT_MAIN)
            canvas.create_text((x0 + x1) / 2, c_height - 10, text=g, font=("Segoe UI", 9, "bold"), fill=COLOR_TEXT_MUTED)

    # =========================================================================
    # Page 2: Student Management Directory
    # =========================================================================
    def show_management_page(self):
        """Render Student Directory table view with search and filters."""
        self._update_nav_highlight("management")
        self._clear_content()

        # Filter & Search Bar
        filter_card = tk.Frame(
            self.content_container,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=18,
            pady=14
        )
        filter_card.pack(fill=tk.X, pady=(0, 12))

        # Search Box
        s_box = tk.Frame(filter_card, bg=COLOR_CARD_SUB, padx=8, pady=4)
        s_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))

        tk.Label(s_box, text="🔍", font=("Segoe UI", 10), bg=COLOR_CARD_SUB, fg=COLOR_TEXT_MUTED).pack(side=tk.LEFT, padx=(0, 6))

        self.search_entry = tk.Entry(
            s_box,
            font=("Segoe UI", 10),
            bg=COLOR_CARD_SUB,
            fg=COLOR_TEXT_MAIN,
            relief=tk.FLAT,
            bd=0
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.insert(0, "Filter by name, ID, or course...")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END) if "Filter by" in self.search_entry.get() else None)
        self.search_entry.bind("<KeyRelease>", lambda e: self._apply_search_and_filter())

        # Course Dropdown
        tk.Label(filter_card, text="Course:", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(side=tk.LEFT, padx=(0, 6))
        courses = ["All"] + self.service.get_unique_courses()
        self.course_filter_var = tk.StringVar(value="All")
        c_combo = ttk.Combobox(filter_card, textvariable=self.course_filter_var, values=courses, state="readonly", width=11)
        c_combo.pack(side=tk.LEFT, padx=(0, 10))
        c_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_search_and_filter())

        # Grade Dropdown
        tk.Label(filter_card, text="Grade:", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(side=tk.LEFT, padx=(0, 6))
        self.grade_filter_var = tk.StringVar(value="All")
        g_combo = ttk.Combobox(filter_card, textvariable=self.grade_filter_var, values=["All", "A+", "A", "B", "C", "D", "F"], state="readonly", width=7)
        g_combo.pack(side=tk.LEFT, padx=(0, 10))
        g_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_search_and_filter())

        # Status Dropdown
        tk.Label(filter_card, text="Status:", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(side=tk.LEFT, padx=(0, 6))
        self.status_filter_var = tk.StringVar(value="All")
        st_combo = ttk.Combobox(filter_card, textvariable=self.status_filter_var, values=["All", "Distinction", "Passing", "Needs Improvement"], state="readonly", width=12)
        st_combo.pack(side=tk.LEFT, padx=(0, 14))
        st_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_search_and_filter())

        # New Student Button
        tk.Button(
            filter_card,
            text="➕ New Student",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_PRIMARY,
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=5,
            cursor="hand2",
            bd=0,
            command=self.open_add_student_modal
        ).pack(side=tk.RIGHT)

        # ---------------- Student Table ----------------
        table_card = tk.Frame(
            self.content_container,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=16,
            pady=14
        )
        table_card.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Name", "Course", "Marks", "Grade", "Status", "Phone", "Email")
        self.student_tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        widths = {"ID": 90, "Name": 160, "Course": 120, "Marks": 80, "Grade": 60, "Status": 120, "Phone": 120, "Email": 170}
        for col, width in widths.items():
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=width, anchor="w")

        scroll = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scroll.set)

        self.student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.student_tree.bind("<Double-1>", lambda e: self._on_tree_double_click())

        # Action Bar Below Table
        btn_bar = tk.Frame(self.content_container, bg=COLOR_CANVAS_BG)
        btn_bar.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            btn_bar,
            text="👁️ View Full Profile",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD_BG,
            fg=COLOR_PRIMARY,
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            bd=0,
            command=self._view_selected_profile
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_bar,
            text="✏️ Edit Record",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD_BG,
            fg=COLOR_TEXT_MAIN,
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            bd=0,
            command=self._edit_selected_student
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_bar,
            text="🗑️ Delete Record",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_DANGER_BG,
            fg=COLOR_DANGER_FG,
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            bd=0,
            command=self._delete_selected_student
        ).pack(side=tk.LEFT)

        self._apply_search_and_filter()

    def _apply_search_and_filter(self):
        query = self.search_entry.get()
        if "Filter by" in query:
            query = ""
        course = self.course_filter_var.get()
        grade = self.grade_filter_var.get()
        status = self.status_filter_var.get() if hasattr(self, "status_filter_var") else "All"

        results = self.service.search_and_filter(query, course, grade, status_filter=status)

        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        for s in results:
            self.student_tree.insert("", tk.END, iid=s.student_id, values=(
                s.student_id,
                s.name,
                s.course,
                f"{s.marks:.1f}%",
                s.get_grade(),
                s.get_status(),
                s.phone or "—",
                s.email or "—"
            ))

    def _get_selected_student_id(self) -> str:
        sel = self.student_tree.selection()
        return sel[0] if sel else ""

    def _on_tree_double_click(self):
        sid = self._get_selected_student_id()
        if sid:
            s = self.service.get_student_by_id(sid)
            if s:
                self._goto_profile(s)

    def _view_selected_profile(self):
        sid = self._get_selected_student_id()
        if not sid:
            messagebox.showinfo("Selection Required", "Please click on a student row from the table first.")
            return
        s = self.service.get_student_by_id(sid)
        if s:
            self._goto_profile(s)

    def _edit_selected_student(self):
        sid = self._get_selected_student_id()
        if not sid:
            messagebox.showinfo("Selection Required", "Please select a student row to edit.")
            return
        s = self.service.get_student_by_id(sid)
        if s:
            self.open_edit_student_modal(s)

    def _delete_selected_student(self):
        sid = self._get_selected_student_id()
        if not sid:
            messagebox.showinfo("Selection Required", "Please select a student record to delete.")
            return

        s = self.service.get_student_by_id(sid)
        if not s:
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete student:\n\n{s.name} (ID: {s.student_id})?\n\nThis record will be removed from students.json.",
            parent=self.root
        )
        if confirm:
            ok, msg = self.service.delete_student(sid)
            if ok:
                messagebox.showinfo("Success", msg)
                self._apply_search_and_filter()
                self._update_nav_highlight(self.current_page)
            else:
                messagebox.showerror("Error", msg)

    # =========================================================================
    # Page 3: Student Profile
    # =========================================================================
    def show_profile_page(self):
        """Render individual student profile card."""
        self._update_nav_highlight("profile")
        self._clear_content()

        container = self._create_scrollable_container()

        # Selector
        sel_card = tk.Frame(
            container,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=18,
            pady=12
        )
        sel_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(sel_card, text="👤 Select Student:", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(side=tk.LEFT, padx=(0, 10))

        all_students = self.service.get_all_students()
        student_choices = [f"{s.student_id} — {s.name} ({s.course})" for s in all_students]

        self.profile_combo_var = tk.StringVar()
        if self.selected_student_for_profile:
            curr_str = f"{self.selected_student_for_profile.student_id} — {self.selected_student_for_profile.name} ({self.selected_student_for_profile.course})"
            self.profile_combo_var.set(curr_str)
        elif student_choices:
            self.profile_combo_var.set(student_choices[0])
            self.selected_student_for_profile = all_students[0]

        combo = ttk.Combobox(sel_card, textvariable=self.profile_combo_var, values=student_choices, state="readonly", width=36)
        combo.pack(side=tk.LEFT)
        combo.bind("<<ComboboxSelected>>", self._on_profile_combo_change)

        if not self.selected_student_for_profile:
            self._render_empty_state(container, "👤", "No Student Selected", "Select a student from the dropdown or register a new record to inspect their profile.")
            return

        s = self.selected_student_for_profile

        # Hero Profile Card
        hero_card = tk.Frame(
            container,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            padx=28,
            pady=24
        )
        hero_card.pack(fill=tk.X, pady=(0, 16))

        h_top = tk.Frame(hero_card, bg=COLOR_CARD_BG)
        h_top.pack(fill=tk.X)

        initials = s.name[:2].upper() if len(s.name) >= 2 else s.name.upper()
        avatar = tk.Label(h_top, text=initials, font=("Segoe UI", 20, "bold"), fg="#FFFFFF", bg=COLOR_PRIMARY, width=3, height=1)
        avatar.pack(side=tk.LEFT, padx=(0, 16))

        info_box = tk.Frame(h_top, bg=COLOR_CARD_BG)
        info_box.pack(side=tk.LEFT)

        tk.Label(info_box, text=s.name, font=("Segoe UI", 18, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(anchor="w")

        meta = tk.Frame(info_box, bg=COLOR_CARD_BG)
        meta.pack(anchor="w", pady=(4, 0))

        tk.Label(meta, text=f"ID: {s.student_id}", font=("Segoe UI", 9, "bold"), fg=COLOR_PRIMARY, bg=COLOR_BADGE_BG, padx=8, pady=2).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(meta, text=f"Course: {s.course}", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_SUB, padx=8, pady=2).pack(side=tk.LEFT, padx=(0, 8))

        status = s.get_status()
        s_bg = COLOR_BADGE_BG if status == "Distinction" else ("#E0F2FE" if status == "Passing" else COLOR_DANGER_BG)
        s_fg = COLOR_PRIMARY if status == "Distinction" else (COLOR_ACCENT if status == "Passing" else COLOR_DANGER_FG)
        tk.Label(meta, text=f"● {status}", font=("Segoe UI", 9, "bold"), fg=s_fg, bg=s_bg, padx=8, pady=2).pack(side=tk.LEFT)

        tk.Button(
            h_top,
            text="✏️ Edit Record",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_PRIMARY,
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            bd=0,
            command=lambda: self.open_edit_student_modal(s)
        ).pack(side=tk.RIGHT)

        # Academic Metrics Split
        grid_row = tk.Frame(container, bg=COLOR_CANVAS_BG)
        grid_row.pack(fill=tk.X, pady=(0, 16))

        m_card = tk.Frame(grid_row, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=16)
        m_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        tk.Label(m_card, text="Academic Percentage", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w")
        tk.Label(m_card, text=f"{s.marks:.1f}%", font=("Segoe UI", 32, "bold"), fg=COLOR_PRIMARY, bg=COLOR_CARD_BG).pack(anchor="w", pady=(6, 2))
        tk.Label(m_card, text="Evaluated out of 100 maximum marks", font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w")

        g_card = tk.Frame(grid_row, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=16)
        g_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        tk.Label(g_card, text="Awarded Grade", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w")
        tk.Label(g_card, text=s.get_grade(), font=("Segoe UI", 32, "bold"), fg=s_fg, bg=COLOR_CARD_BG).pack(anchor="w", pady=(6, 2))
        tk.Label(g_card, text=f"Standing: {s.get_status()}", font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w")

        # Contact Details Card
        c_card = tk.Frame(container, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=24, pady=20)
        c_card.pack(fill=tk.X)
        tk.Label(c_card, text="📋 Student Information & Records", font=("Segoe UI", 12, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(anchor="w", pady=(0, 12))

        rows = [
            ("Student ID", s.student_id),
            ("Full Name", s.name),
            ("Enrolled Course", s.course),
            ("Email Address", s.email or "Not registered"),
            ("Phone Contact", s.phone or "Not registered"),
            ("Enrollment Date", s.enrollment_date or datetime.now().strftime("%Y-%m-%d")),
        ]

        for lbl, val in rows:
            r = tk.Frame(c_card, bg=COLOR_CARD_SUB, padx=14, pady=8)
            r.pack(fill=tk.X, pady=(0, 6))
            tk.Label(r, text=lbl, font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_SUB).pack(side=tk.LEFT)
            tk.Label(r, text=val, font=("Segoe UI", 9), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_SUB).pack(side=tk.RIGHT)

    def _goto_profile(self, student: Student):
        self.selected_student_for_profile = student
        self.show_profile_page()

    def _on_profile_combo_change(self, event):
        val = self.profile_combo_var.get()
        if " — " in val:
            sid = val.split(" — ")[0].strip()
            s = self.service.get_student_by_id(sid)
            if s:
                self.selected_student_for_profile = s
                self.show_profile_page()

    # =========================================================================
    # Page 4: Academic Performance
    # =========================================================================
    def show_academic_page(self):
        """Render Academic Performance analytics."""
        self._update_nav_highlight("academic")
        self._clear_content()

        container = self._create_scrollable_container()
        metrics = self.service.get_dashboard_metrics()

        tk.Label(container, text="📈 Academic Performance & Tier Rankings", font=("Segoe UI", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CANVAS_BG).pack(anchor="w", pady=(0, 4))
        tk.Label(container, text="Cohort statistics, grade distribution, and academic honor roll.", font=("Segoe UI", 10), fg=COLOR_TEXT_MUTED, bg=COLOR_CANVAS_BG).pack(anchor="w", pady=(0, 16))

        # Cohort Summary
        stat_card = tk.Frame(container, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=16)
        stat_card.pack(fill=tk.X, pady=(0, 16))
        tk.Label(stat_card, text="📊 Cohort Metrics", font=("Segoe UI", 12, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(anchor="w", pady=(0, 10))

        s_row = tk.Frame(stat_card, bg=COLOR_CARD_BG)
        s_row.pack(fill=tk.X)

        s_items = [
            ("Average Marks", f"{metrics['average_marks']}%"),
            ("Highest Mark", f"{metrics['highest_marks']}%"),
            ("Lowest Mark", f"{metrics['lowest_marks']}%"),
            ("Passing Rate", f"{metrics['passing_rate']}%"),
            ("Total Students", str(metrics["total_students"])),
        ]

        for title, val in s_items:
            b = tk.Frame(s_row, bg=COLOR_CARD_SUB, padx=14, pady=10)
            b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
            tk.Label(b, text=title, font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_SUB).pack(anchor="w")
            tk.Label(b, text=val, font=("Segoe UI", 16, "bold"), fg=COLOR_PRIMARY, bg=COLOR_CARD_SUB).pack(anchor="w", pady=(4, 0))

        # Honor Roll Card
        honor_card = tk.Frame(container, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=20, pady=16)
        honor_card.pack(fill=tk.X, pady=(0, 16))
        tk.Label(honor_card, text="🏆 Top Academic Honor Roll", font=("Segoe UI", 12, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(anchor="w", pady=(0, 10))

        students_sorted = sorted(self.service.get_all_students(), key=lambda s: s.marks, reverse=True)

        if not students_sorted:
            tk.Label(honor_card, text="No records available.", font=("Segoe UI", 9, "italic"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w")
        else:
            for rank, s in enumerate(students_sorted[:10], start=1):
                rf = tk.Frame(honor_card, bg=COLOR_CARD_SUB, padx=14, pady=8)
                rf.pack(fill=tk.X, pady=(0, 4))

                badge = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else f"#{rank}"))
                tk.Label(rf, text=badge, font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARY, bg=COLOR_CARD_SUB, width=4).pack(side=tk.LEFT)
                tk.Label(rf, text=s.name, font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_SUB, width=22, anchor="w").pack(side=tk.LEFT, padx=10)
                tk.Label(rf, text=f"Course: {s.course}", font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_SUB, width=16, anchor="w").pack(side=tk.LEFT)
                tk.Label(rf, text=f"{s.marks:.1f}% ({s.get_grade()})", font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARY, bg=COLOR_CARD_SUB).pack(side=tk.RIGHT)

    # =========================================================================
    # Page 5: Reports & Export
    # =========================================================================
    def show_reports_page(self):
        """Render Reports and CSV export page."""
        self._update_nav_highlight("reports")
        self._clear_content()

        container = self._create_scrollable_container()

        tk.Label(container, text="📑 Academic Reports & Data Export", font=("Segoe UI", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CANVAS_BG).pack(anchor="w", pady=(0, 4))
        tk.Label(container, text="Generate CSV spreadsheets and check persistence diagnostics.", font=("Segoe UI", 10), fg=COLOR_TEXT_MUTED, bg=COLOR_CANVAS_BG).pack(anchor="w", pady=(0, 16))

        # CSV Export Card
        exp_card = tk.Frame(container, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=24, pady=20)
        exp_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(exp_card, text="📥 Export Student Directory to CSV", font=("Segoe UI", 12, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(anchor="w")
        tk.Label(exp_card, text="Generates a standardized CSV spreadsheet report with IDs, names, courses, marks, and grades.", font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w", pady=(4, 12))

        tk.Button(
            exp_card,
            text="Export to CSV Now",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_PRIMARY,
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=18,
            pady=8,
            cursor="hand2",
            bd=0,
            command=self._export_csv_action
        ).pack(anchor="w")

        # Diagnostics Card
        diag_card = tk.Frame(container, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=24, pady=20)
        diag_card.pack(fill=tk.X)

        tk.Label(diag_card, text="💾 Storage & Persistence Diagnostics", font=("Segoe UI", 12, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(anchor="w", pady=(0, 10))

        stats = self.storage.get_storage_stats()
        diag_text = (
            f"• Database File: {stats['storage_file']}\n"
            f"• File Size: {stats['size_bytes']} bytes\n"
            f"• Automated Backup: {'Active (students_backup.json present)' if stats['backup_exists'] else 'No backup created'}\n"
            f"• Total Saved Records: {len(self.service.get_all_students())} students\n"
            f"• Architecture: Pure Python Standard Library (zero external dependencies)"
        )
        tk.Label(diag_card, text=diag_text, font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG, justify=tk.LEFT).pack(anchor="w")

    def _export_csv_action(self):
        default_name = f"studenthub_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")],
            initialfile=default_name,
            title="Save Student Directory as CSV"
        )
        if path:
            result = self.service.export_csv(path)
            if result and os.path.exists(result):
                messagebox.showinfo("Export Successful", f"Records exported successfully to:\n\n{result}")
            else:
                messagebox.showerror("Export Error", "Failed to write CSV.")

    def _quick_export_csv(self):
        result = self.service.export_csv()
        if result:
            messagebox.showinfo("Export Successful", f"Records exported to:\n\n{result}")

    # =========================================================================
    # Page 6: Settings
    # =========================================================================
    def show_settings_page(self):
        """Render settings and grade scale reference."""
        self._update_nav_highlight("settings")
        self._clear_content()

        container = self._create_scrollable_container()

        tk.Label(container, text="⚙️ Preferences & Configuration", font=("Segoe UI", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CANVAS_BG).pack(anchor="w", pady=(0, 4))
        tk.Label(container, text="Academic grading reference and enterprise system status.", font=("Segoe UI", 10), fg=COLOR_TEXT_MUTED, bg=COLOR_CANVAS_BG).pack(anchor="w", pady=(0, 16))

        # Grading Scale
        scale_card = tk.Frame(container, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=24, pady=20)
        scale_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(scale_card, text="📊 Academic Grading Reference Scale", font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack(anchor="w", pady=(0, 10))

        scale_items = [
            ("A+ (Outstanding)", "90.0% – 100.0%", "Distinction"),
            ("A (Excellent)", "80.0% – 89.9%", "Distinction"),
            ("B (Good)", "70.0% – 79.9%", "Passing"),
            ("C (Satisfactory)", "60.0% – 69.9%", "Passing"),
            ("D (Pass)", "50.0% – 59.9%", "Passing"),
            ("F (Fail)", "Below 50.0%", "Needs Improvement"),
        ]

        for grade, marks_range, standing in scale_items:
            r = tk.Frame(scale_card, bg=COLOR_CARD_SUB, padx=12, pady=6)
            r.pack(fill=tk.X, pady=(0, 4))
            tk.Label(r, text=grade, font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_SUB, width=18, anchor="w").pack(side=tk.LEFT)
            tk.Label(r, text=marks_range, font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_SUB, width=18, anchor="w").pack(side=tk.LEFT)
            tk.Label(r, text=standing, font=("Segoe UI", 9, "bold"), fg=COLOR_PRIMARY, bg=COLOR_CARD_SUB).pack(side=tk.RIGHT)

    # =========================================================================
    # Modals: Add / Edit
    # =========================================================================
    def open_add_student_modal(self):
        self._build_student_form_modal("Add New Student Record", is_edit=False)

    def open_edit_student_modal(self, student: Student):
        self._build_student_form_modal("Update Student Record", is_edit=True, student=student)

    def _build_student_form_modal(self, title: str, is_edit: bool, student=None):
        modal = tk.Toplevel(self.root)
        modal.title(title)
        modal.geometry("480x620")
        modal.resizable(False, False)
        modal.configure(bg=COLOR_CARD_BG)
        modal.transient(self.root)
        modal.grab_set()

        tk.Label(modal, text=title, font=("Segoe UI", 14, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG, pady=16).pack(fill=tk.X, padx=24)

        form = tk.Frame(modal, bg=COLOR_CARD_BG)
        form.pack(fill=tk.BOTH, expand=True, padx=28)

        # ID
        tk.Label(form, text="Student ID *", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w", pady=(0, 2))
        id_entry = tk.Entry(form, font=("Segoe UI", 10), bg=COLOR_CARD_SUB, fg=COLOR_TEXT_MAIN, relief=tk.FLAT, bd=0)
        id_entry.pack(fill=tk.X, ipady=6, pady=(0, 8))
        if is_edit and student:
            id_entry.insert(0, student.student_id)
            id_entry.configure(state="disabled")

        # Name
        tk.Label(form, text="Full Name *", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w", pady=(0, 2))
        name_entry = tk.Entry(form, font=("Segoe UI", 10), bg=COLOR_CARD_SUB, fg=COLOR_TEXT_MAIN, relief=tk.FLAT, bd=0)
        name_entry.pack(fill=tk.X, ipady=6, pady=(0, 8))
        if is_edit and student:
            name_entry.insert(0, student.name)

        # Course
        tk.Label(form, text="Course *", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w", pady=(0, 2))
        course_entry = tk.Entry(form, font=("Segoe UI", 10), bg=COLOR_CARD_SUB, fg=COLOR_TEXT_MAIN, relief=tk.FLAT, bd=0)
        course_entry.pack(fill=tk.X, ipady=6, pady=(0, 8))
        if is_edit and student:
            course_entry.insert(0, student.course)

        # Marks
        tk.Label(form, text="Academic Marks (0 - 100) *", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w", pady=(0, 2))
        marks_entry = tk.Entry(form, font=("Segoe UI", 10), bg=COLOR_CARD_SUB, fg=COLOR_TEXT_MAIN, relief=tk.FLAT, bd=0)
        marks_entry.pack(fill=tk.X, ipady=6, pady=(0, 8))
        if is_edit and student:
            marks_entry.insert(0, str(student.marks))

        # Phone
        tk.Label(form, text="Phone Number (Optional)", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w", pady=(0, 2))
        phone_entry = tk.Entry(form, font=("Segoe UI", 10), bg=COLOR_CARD_SUB, fg=COLOR_TEXT_MAIN, relief=tk.FLAT, bd=0)
        phone_entry.pack(fill=tk.X, ipady=6, pady=(0, 8))
        if is_edit and student and student.phone:
            phone_entry.insert(0, student.phone)

        # Email
        tk.Label(form, text="Email Address (Optional)", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG).pack(anchor="w", pady=(0, 2))
        email_entry = tk.Entry(form, font=("Segoe UI", 10), bg=COLOR_CARD_SUB, fg=COLOR_TEXT_MAIN, relief=tk.FLAT, bd=0)
        email_entry.pack(fill=tk.X, ipady=6, pady=(0, 8))
        if is_edit and student and student.email:
            email_entry.insert(0, student.email)

        btn_row = tk.Frame(modal, bg=COLOR_CARD_BG, pady=16)
        btn_row.pack(fill=tk.X, padx=28)

        def _save():
            sid = id_entry.get().strip() if not is_edit else student.student_id
            name = name_entry.get().strip()
            course = course_entry.get().strip()
            m_str = marks_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()

            if is_edit:
                try:
                    m_val = float(m_str) if m_str else student.marks
                except ValueError:
                    messagebox.showerror("Validation Error", "Marks must be a valid number.", parent=modal)
                    return
                ok, msg = self.service.update_student(sid, name=name, course=course, marks=m_val, email=email, phone=phone)
            else:
                try:
                    m_val = float(m_str)
                except ValueError:
                    messagebox.showerror("Validation Error", "Marks must be a valid number.", parent=modal)
                    return
                ok, msg = self.service.add_student(sid, name, course, m_val, email=email, phone=phone)

            if ok:
                messagebox.showinfo("Success", msg, parent=modal)
                modal.destroy()
                getattr(self, f"show_{self.current_page}_page", self.show_dashboard_page)()
            else:
                messagebox.showerror("Error", msg, parent=modal)

        tk.Button(btn_row, text="Save Record", font=("Segoe UI", 10, "bold"), bg=COLOR_PRIMARY, fg="#FFFFFF", relief=tk.FLAT, padx=18, pady=7, cursor="hand2", bd=0, command=_save).pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(btn_row, text="Cancel", font=("Segoe UI", 10), bg=COLOR_CARD_SUB, fg=COLOR_TEXT_MUTED, relief=tk.FLAT, padx=14, pady=7, cursor="hand2", bd=0, command=modal.destroy).pack(side=tk.RIGHT)

    def _render_empty_state(self, parent: tk.Frame, icon: str, title: str, description: str):
        card = tk.Frame(parent, bg=COLOR_CARD_BG, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=28, pady=36)
        card.pack(fill=tk.X, pady=(0, 16))
        tk.Label(card, text=icon, font=("Segoe UI", 36), bg=COLOR_CARD_BG).pack(pady=(0, 8))
        tk.Label(card, text=title, font=("Segoe UI", 14, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG).pack()
        tk.Label(card, text=description, font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG, wraplength=480, justify=tk.CENTER).pack(pady=(4, 0))


def launch_gui():
    """Launch the Enterprise StudentHub desktop portal."""
    root = tk.Tk()
    app = StudentHubGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
