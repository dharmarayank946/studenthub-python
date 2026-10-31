"""Tests for StudentHub FastAPI Backend Authentication & User Profile Endpoints."""

import os
import sys
import unittest
import tempfile
from fastapi.testclient import TestClient

# Ensure root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "backend"))

from auth import AuthManager
import backend.main as backend_module


class TestBackendAuthEndpoints(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db = os.path.join(self.temp_dir.name, "test_users.db")
        # Swap auth_manager with test instance
        self.orig_auth_manager = backend_module.auth_manager
        backend_module.auth_manager = AuthManager(db_path=self.test_db)
        self.client = TestClient(backend_module.app)

    def tearDown(self):
        backend_module.auth_manager = self.orig_auth_manager
        self.temp_dir.cleanup()

    def test_default_admin_login(self):
        response = self.client.post("/api/v1/auth/login", json={
            "identifier": "admin",
            "password": "Admin@123"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["username"], "admin")
        self.assertEqual(data["user"]["role"], "Administrator")

    def test_register_and_login_new_user(self):
        reg_resp = self.client.post("/api/v1/auth/register", json={
            "username": "prof_smith",
            "email": "smith@studenthub.edu",
            "password": "ProfessorPassword123",
            "full_name": "Prof. Alan Smith",
            "department": "Mathematics",
            "phone": "+1 555-4321",
            "bio": "Senior Lecturer in Pure Mathematics."
        })
        self.assertEqual(reg_resp.status_code, 200)
        user_id = reg_resp.json()["user"]["id"]

        # Login with email
        login_resp = self.client.post("/api/v1/auth/login", json={
            "identifier": "smith@studenthub.edu",
            "password": "ProfessorPassword123"
        })
        self.assertEqual(login_resp.status_code, 200)
        self.assertEqual(login_resp.json()["user"]["id"], user_id)

    def test_profile_update(self):
        # Update admin profile
        update_resp = self.client.put("/api/v1/auth/profile/1", json={
            "full_name": "Chief Administrator",
            "email": "chief.admin@studenthub.edu",
            "department": "Computer Science & IT",
            "phone": "+1 800-555-0199",
            "bio": "Updated administrator biography."
        })
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json()["user"]["full_name"], "Chief Administrator")

        # Verify via GET profile
        get_resp = self.client.get("/api/v1/auth/profile/1")
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json()["user"]["department"], "Computer Science & IT")

    def test_change_password(self):
        # Change admin password
        pwd_resp = self.client.post("/api/v1/auth/change-password/1", json={
            "old_password": "Admin@123",
            "new_password": "NewAdminPassword987"
        })
        self.assertEqual(pwd_resp.status_code, 200)

        # Login with old should fail
        fail_login = self.client.post("/api/v1/auth/login", json={
            "identifier": "admin",
            "password": "Admin@123"
        })
        self.assertEqual(fail_login.status_code, 401)

        # Login with new should succeed
        success_login = self.client.post("/api/v1/auth/login", json={
            "identifier": "admin",
            "password": "NewAdminPassword987"
        })
        self.assertEqual(success_login.status_code, 200)


if __name__ == "__main__":
    unittest.main()

