import os
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("JWT_SECRET", "test-secret-at-least-32-bytes-long")

import jwt

from app import JWT_ALGORITHM, MAX_WORK_UNITS, app, get_jwt_secret


def fake_database(row):
    connection = MagicMock()
    connection.__enter__.return_value.execute.return_value.fetchone.return_value = row
    return connection


def make_token(user_id):
    return jwt.encode({"sub": str(user_id)}, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def auth_header(user_id):
    return {"Authorization": f"Bearer {make_token(user_id)}"}


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_demo_work_returns_checksum(self):
        response = self.client.get("/api/demo/work?units=4")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"units": 4, "checksum": 14})

    def test_demo_work_rejects_invalid_or_unbounded_units(self):
        invalid = self.client.get("/api/demo/work?units=many")
        too_large = self.client.get(f"/api/demo/work?units={MAX_WORK_UNITS + 1}")

        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(too_large.status_code, 400)

    def test_metrics_endpoint_is_available(self):
        self.client.get("/healthz")
        response = self.client.get("/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertIn("app_http_requests_total", response.get_data(as_text=True))

    def test_tasks_endpoints_require_authentication(self):
        for method, path in [
            ("get", "/api/tasks"),
            ("post", "/api/tasks"),
            ("get", "/api/tasks/search"),
            ("patch", "/api/tasks/1"),
            ("delete", "/api/tasks/1"),
        ]:
            response = getattr(self.client, method)(path)
            self.assertEqual(response.status_code, 401, path)

    def test_register_hashes_the_password(self):
        connection = fake_database(None)
        connection.__enter__.return_value.execute.return_value.fetchone.return_value = {
            "id": 1,
            "username": "alice",
        }

        with patch("app.connect_to_database", return_value=connection):
            response = self.client.post(
                "/api/auth/register", json={"username": "alice", "password": "correct-horse"}
            )

        self.assertEqual(response.status_code, 201)
        _sql, params = connection.__enter__.return_value.execute.call_args.args
        self.assertNotIn("correct-horse", params)

    def test_register_rejects_a_short_password(self):
        response = self.client.post(
            "/api/auth/register", json={"username": "alice", "password": "short"}
        )

        self.assertEqual(response.status_code, 400)

    def test_delete_task_returns_deleted_task(self):
        task = {"id": 7, "title": "Write tests", "done": False}

        with patch("app.connect_to_database", return_value=fake_database(task)):
            response = self.client.delete("/api/tasks/7", headers=auth_header(user_id=42))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, task)

    def test_delete_missing_task_returns_404(self):
        with patch("app.connect_to_database", return_value=fake_database(None)):
            response = self.client.delete("/api/tasks/999", headers=auth_header(user_id=42))

        self.assertEqual(response.status_code, 404)

    def test_delete_task_is_scoped_to_the_caller(self):
        connection = fake_database(None)

        with patch("app.connect_to_database", return_value=connection):
            response = self.client.delete("/api/tasks/1", headers=auth_header(user_id=42))

        self.assertEqual(response.status_code, 404)
        sql, params = connection.__enter__.return_value.execute.call_args.args
        self.assertIn("owner_id", sql)
        self.assertEqual(params, (1, 42))

    def test_update_task_is_scoped_to_the_caller(self):
        task = {"id": 1, "title": "Write tests", "done": True}
        connection = fake_database(task)

        with patch("app.connect_to_database", return_value=connection):
            response = self.client.patch(
                "/api/tasks/1", json={"done": True}, headers=auth_header(user_id=42)
            )

        self.assertEqual(response.status_code, 200)
        sql, params = connection.__enter__.return_value.execute.call_args.args
        self.assertIn("owner_id", sql)
        self.assertEqual(params, (True, 1, 42))

    def test_search_passes_term_as_query_parameter(self):
        payload = "' OR '1'='1"
        connection = MagicMock()
        execute = connection.__enter__.return_value.execute
        execute.return_value.fetchall.return_value = []

        with patch("app.connect_to_database", return_value=connection):
            response = self.client.get(
                "/api/tasks/search", query_string={"q": payload}, headers=auth_header(user_id=42)
            )

        self.assertEqual(response.status_code, 200)
        sql, params = execute.call_args.args
        self.assertNotIn(payload, sql)
        self.assertEqual(params, (42, f"%{payload}%"))


if __name__ == "__main__":
    unittest.main()
