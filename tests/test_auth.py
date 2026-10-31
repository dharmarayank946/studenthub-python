"""Automated Unit Tests for StudentHub Authentication & Profile Engine."""

import os
import shutil
import tempfile
import unittest

from auth import AuthManager


class TestAuthManager(unittest.TestCase):
    """Test suite for user registration, authentication, and profile management."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_users.db")
        self.auth = AuthManager(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_default_admin_seeded(self):
        """Verify initial admin account is created."""
        success, msg, user = self.auth.login("admin", "Admin@123")
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "admin")
        self.assertEqual(user["email"], "admin@studenthub.edu")

    def test_registration_success(self):
        """Verify successful user registration."""
        success, msg, user = self.auth.register(
            username="prof_smith",
            email="smith@university.edu",
            full_name="Dr. John Smith",
            password="SecurePassword123",
            confirm_password="SecurePassword123",
            role="Faculty",
            department="Physics"
        )
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "prof_smith")
        self.assertEqual(user["department"], "Physics")

    def test_registration_duplicate_username_rejected(self):
        """Prevent duplicate usernames."""
        self.auth.register("janedoe", "jane1@edu.com", "Jane Doe", "pass123", "pass123")
        success, msg, user = self.auth.register("janedoe", "jane2@edu.com", "Jane Duplicate", "pass123", "pass123")
        self.assertFalse(success)
        self.assertIn("already registered", msg)

    def test_registration_duplicate_email_rejected(self):
        """Prevent duplicate email addresses."""
        self.auth.register("user_a", "shared@edu.com", "User A", "pass123", "pass123")
        success, msg, user = self.auth.register("user_b", "shared@edu.com", "User B", "pass123", "pass123")
        self.assertFalse(success)
        self.assertIn("already registered", msg)

    def test_registration_password_mismatch(self):
        """Ensure password confirmation mismatch is rejected."""
        success, msg, user = self.auth.register("test_user", "test@edu.com", "Test User", "Password123", "Mismatch456")
        self.assertFalse(success)
        self.assertIn("does not match", msg)

    def test_login_via_username_and_email(self):
        """Verify login works using both username and email."""
        self.auth.register("clark_kent", "clark@dailyplanet.com", "Clark Kent", "Krypton123", "Krypton123")

        # Login with username
        ok_u, msg_u, user_u = self.auth.login("clark_kent", "Krypton123")
        self.assertTrue(ok_u)
        self.assertEqual(user_u["full_name"], "Clark Kent")

        # Login with email
        ok_e, msg_e, user_e = self.auth.login("clark@dailyplanet.com", "Krypton123")
        self.assertTrue(ok_e)
        self.assertEqual(user_e["username"], "clark_kent")

    def test_login_invalid_password_rejected(self):
        """Ensure wrong password fails authentication."""
        self.auth.register("bruce_wayne", "bruce@wayne.com", "Bruce Wayne", "Batmobile123", "Batmobile123")
        success, msg, user = self.auth.login("bruce_wayne", "WrongPassword")
        self.assertFalse(success)
        self.assertIn("Invalid", msg)

    def test_profile_update(self):
        """Verify user can view and update their profile."""
        _, _, user = self.auth.register("tony_stark", "tony@stark.com", "Tony Stark", "Jarvis123", "Jarvis123", department="Robotics")
        user_id = user["id"]

        success, msg, updated = self.auth.update_profile(
            user_id=user_id,
            full_name="Sir Anthony Stark",
            email="ceo@starkindustries.com",
            department="Advanced AI",
            phone="+1 212 555 0100",
            bio="Genius, billionaire, educator."
        )
        self.assertTrue(success)
        self.assertEqual(updated["full_name"], "Sir Anthony Stark")
        self.assertEqual(updated["department"], "Advanced AI")
        self.assertEqual(updated["email"], "ceo@starkindustries.com")

    def test_change_password(self):
        """Verify password change with current password check."""
        _, _, user = self.auth.register("peter_parker", "peter@dailybugle.com", "Peter Parker", "OldPass123", "OldPass123")
        user_id = user["id"]

        # Wrong old password
        bad_change, bad_msg = self.auth.change_password(user_id, "WrongOld", "NewPass123", "NewPass123")
        self.assertFalse(bad_change)

        # Correct old password
        ok_change, ok_msg = self.auth.change_password(user_id, "OldPass123", "NewPass123", "NewPass123")
        self.assertTrue(ok_change)

        # Verify old password no longer works
        old_login, _, _ = self.auth.login("peter_parker", "OldPass123")
        self.assertFalse(old_login)

        # Verify new password works
        new_login, _, _ = self.auth.login("peter_parker", "NewPass123")
        self.assertTrue(new_login)


if __name__ == "__main__":
    unittest.main()

