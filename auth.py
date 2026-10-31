"""StudentHub — Authentication and User Profile Management Engine.
==================================================================
Implements secure user authentication, registration, profile editing,
and password management using an isolated SQLite database and PBKDF2-HMAC-SHA256
salted password hashing.

Features:
- User Registration with password confirmation, email & username uniqueness validation.
- Login using either Username or Email with secure password verification.
- User Profile viewing and editing (Full Name, Email, Department, Phone, Bio).
- Password change functionality with old password verification.
- Complete isolation: Stores user account data in `users.db` without affecting
  student academic records (`students.json`).
- Pre-seeds an initial administrator account if database is freshly initialized.
"""

import os
import re
import hmac
import sqlite3
import hashlib
import contextlib
from datetime import datetime
from typing import Optional, Dict, Any, Tuple


class AuthManager:
    """Manages user registration, authentication, sessions, and user profiles."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "users.db")
        else:
            self.db_path = db_path

        self._init_db()

    @contextlib.contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Create users table if not exists, and seed default admin user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'Administrator',
                    department TEXT DEFAULT 'Computer Science',
                    phone TEXT DEFAULT '',
                    bio TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    last_login TEXT
                )
            """)
            conn.commit()

            # Check if any user exists; if not, seed default admin account
            cursor.execute("SELECT COUNT(*) as count FROM users")
            count = cursor.fetchone()["count"]
            if count == 0:
                self._seed_default_admin(cursor)
                conn.commit()

    def _seed_default_admin(self, cursor: sqlite3.Cursor):
        """Seed default admin account for initial access."""
        default_username = "admin"
        default_email = "admin@studenthub.edu"
        default_name = "System Administrator"
        default_password = "Admin@123"
        pwd_hash = self.hash_password(default_password)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO users (username, email, full_name, password_hash, role, department, phone, bio, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            default_username,
            default_email,
            default_name,
            pwd_hash,
            "Administrator",
            "Academic Operations",
            "+1 (555) 019-2834",
            "Lead Administrator managing StudentHub records and faculty portal.",
            now_str
        ))

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using PBKDF2-HMAC-SHA256 with a cryptographically secure random salt."""
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return f"{salt.hex()}${key.hex()}"

    @staticmethod
    def verify_password(stored_hash: str, provided_password: str) -> bool:
        """Verify provided password against stored salt$hash string."""
        try:
            parts = stored_hash.split("$")
            if len(parts) != 2:
                return False
            salt_hex, key_hex = parts
            salt = bytes.fromhex(salt_hex)
            expected_key = bytes.fromhex(key_hex)
            actual_key = hashlib.pbkdf2_hmac("sha256", provided_password.encode("utf-8"), salt, 100000)
            return hmac.compare_digest(actual_key, expected_key)
        except Exception:
            return False

    def register(
        self,
        username: str,
        email: str,
        full_name: str,
        password: str,
        confirm_password: str,
        role: str = "Faculty",
        department: str = "Computer Science",
        phone: str = "",
        bio: str = ""
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Register a new user account with complete input validation and duplicate protection."""
        u = username.strip()
        e = email.strip().lower()
        fn = full_name.strip()

        # Validation checks
        if not u or len(u) < 3:
            return False, "Username must be at least 3 characters long.", None
        if not re.match(r"^[a-zA-Z0-9_.-]+$", u):
            return False, "Username can only contain alphanumeric characters, underscores, and dots.", None

        if not e or "@" not in e or "." not in e.split("@")[-1]:
            return False, "Please provide a valid email address.", None

        if not fn or len(fn) < 2:
            return False, "Please enter your full name.", None

        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters long.", None

        if password != confirm_password:
            return False, "Password confirmation does not match.", None

        # Check for existing username or email
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (u,))
            if cursor.fetchone():
                return False, f"Username '{u}' is already registered. Please choose another.", None

            cursor.execute("SELECT id FROM users WHERE email = ?", (e,))
            if cursor.fetchone():
                return False, f"Email address '{e}' is already registered.", None

            pwd_hash = self.hash_password(password)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO users (username, email, full_name, password_hash, role, department, phone, bio, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (u, e, fn, pwd_hash, role or "Faculty", department or "General", phone.strip(), bio.strip(), now_str))
            conn.commit()

            new_id = cursor.lastrowid
            user_data = self.get_user_by_id(new_id)
            return True, "Account created successfully! You can now log in.", user_data

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: str = "Faculty",
        department: str = "Computer Science",
        phone: str = "",
        bio: str = ""
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Convenience wrapper for API user registration."""
        return self.register(
            username=username,
            email=email,
            full_name=full_name,
            password=password,
            confirm_password=password,
            role=role,
            department=department,
            phone=phone,
            bio=bio
        )

    def authenticate_user(self, identifier: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Convenience wrapper for API login."""
        return self.login(identifier, password)

    def update_user_profile(
        self,
        user_id: int,
        full_name: str,
        email: str,
        department: str = "",
        phone: str = "",
        bio: str = ""
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Convenience wrapper for API profile updating."""
        return self.update_profile(user_id, full_name, email, department, phone, bio)

    def change_user_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Convenience wrapper for API password change."""
        return self.change_password(user_id, old_password, new_password, new_password)

    def login(self, username_or_email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Authenticate user by username or email and password."""
        ident = username_or_email.strip()
        if not ident:
            return False, "Username or email is required.", None
        if not password:
            return False, "Password is required.", None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users WHERE username = ? OR email = ?
            """, (ident, ident.lower()))
            row = cursor.fetchone()

            if not row:
                return False, "Invalid username/email or password.", None

            stored_hash = row["password_hash"]
            if not self.verify_password(stored_hash, password):
                return False, "Invalid username/email or password.", None

            # Update last login timestamp
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (now_str, row["id"]))
            conn.commit()

            user_dict = dict(row)
            user_dict.pop("password_hash", None)
            user_dict["last_login"] = now_str
            return True, "Login successful.", user_dict

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch user profile by user ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            user_dict = dict(row)
            user_dict.pop("password_hash", None)
            return user_dict

    def update_profile(
        self,
        user_id: int,
        full_name: str,
        email: str,
        department: str = "",
        phone: str = "",
        bio: str = ""
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Update profile details for an existing user."""
        fn = full_name.strip()
        e = email.strip().lower()

        if not fn or len(fn) < 2:
            return False, "Full name cannot be empty.", None

        if not e or "@" not in e or "." not in e.split("@")[-1]:
            return False, "Please enter a valid email address.", None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Ensure email is not used by another user
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (e, user_id))
            if cursor.fetchone():
                return False, f"Email address '{e}' is already in use by another account.", None

            cursor.execute("""
                UPDATE users
                SET full_name = ?, email = ?, department = ?, phone = ?, bio = ?
                WHERE id = ?
            """, (fn, e, department.strip(), phone.strip(), bio.strip(), user_id))
            conn.commit()

            updated = self.get_user_by_id(user_id)
            return True, "Profile details updated successfully.", updated

    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
        confirm_new_password: str
    ) -> Tuple[bool, str]:
        """Safely update user password after validating current password."""
        if not current_password:
            return False, "Current password is required."

        if not new_password or len(new_password) < 6:
            return False, "New password must be at least 6 characters long."

        if new_password != confirm_new_password:
            return False, "New password confirmation does not match."

        if current_password == new_password:
            return False, "New password cannot be identical to the current password."

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return False, "User not found."

            if not self.verify_password(row["password_hash"], current_password):
                return False, "Incorrect current password."

            new_hash = self.hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
            conn.commit()

            return True, "Password changed successfully."
