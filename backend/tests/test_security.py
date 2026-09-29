"""Regression checks for account isolation and static-file boundaries."""
import asyncio
import unittest

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.db_engine import get_db
from database.db_models import Base
from main import app, serve_spa


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        session_factory = sessionmaker(bind=self.engine)

        def test_db():
            with session_factory() as db:
                yield db

        app.dependency_overrides[get_db] = test_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def _register_and_login(self, username):
        credentials = {"username": username, "password": "Password123!", "phone": "081234567890"}
        self.assertEqual(self.client.post("/api/users/register", json=credentials).status_code, 200)
        response = self.client.post("/api/users/login", json=credentials)
        self.assertEqual(response.status_code, 200)
        return {"Authorization": f"Bearer {response.json()['token']}"}

    def test_private_data_requires_matching_account(self):
        alice = self._register_and_login("alice")
        bob = self._register_and_login("bob")
        self.assertEqual(self.client.get("/api/users/alice/profile").status_code, 401)
        self.assertEqual(self.client.get("/api/users/alice/profile", headers=bob).status_code, 403)
        self.assertEqual(self.client.get("/api/users/alice/profile", headers=alice).status_code, 200)
        self.assertEqual(self.client.get("/api/users/me", headers=alice).json()["username"], "alice")
        self.assertEqual(self.client.post("/api/chat/session", json={"username": "bob", "message": "halo"}, headers=alice).status_code, 403)
        self.assertEqual(self.client.post("/api/chat", json={"message": "halo"}).status_code, 401)
        self.assertEqual(self.client.post("/api/chat/stream", json={"message": "halo"}).status_code, 401)
        self.assertEqual(self.client.post("/api/plans/generate", json={}).status_code, 401)
        self.assertEqual(self.client.post("/api/whatsapp/send-plan", json={"phone": "081234567890", "plan_type": "workout", "title": "A"}).status_code, 401)
        self.assertEqual(self.client.get("/api/workout/gif/all").status_code, 401)

    def test_invalid_token_and_path_are_rejected(self):
        alice = self._register_and_login("alice")
        forged = {"Authorization": alice["Authorization"] + "x"}
        self.assertEqual(self.client.get("/api/users/me", headers=forged).status_code, 401)
        with self.assertRaises(HTTPException) as error:
            asyncio.run(serve_spa("../.env"))
        self.assertEqual(error.exception.status_code, 404)

    def test_workout_dataset_routes_handle_empty_database(self):
        self.assertEqual(self.client.get("/api/workout/body-parts").json()["data"], [])
        self.assertEqual(self.client.get("/api/workout/muscles").json()["data"], [])
        response = self.client.get("/api/workout/generate-split")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["success"])

    def test_whatsapp_plan_limits_nested_content(self):
        alice = self._register_and_login("alice")
        oversized_day = {"day": "Senin", "focus": "Kekuatan", "exercises": [
            {"name": "Push up", "sets": 3, "reps": "10"} for _ in range(31)
        ]}
        response = self.client.post("/api/whatsapp/send-plan", json={
            "plan_type": "workout", "title": "Program", "schedule": [oversized_day]
        }, headers=alice)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
