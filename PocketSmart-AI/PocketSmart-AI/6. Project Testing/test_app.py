import base64
import io
import json
import os
import sys
import tempfile
import unittest
import uuid
from unittest.mock import Mock, patch
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_DIR = PROJECT_ROOT / "5. Project Development Phase"
DATABASE_FILE = Path(tempfile.gettempdir()) / f"pocketsmart-tests-{uuid.uuid4().hex}.sqlite3"
os.environ["DATABASE_PATH"] = str(DATABASE_FILE)
os.environ["GEMINI_API_KEY"] = ""
os.environ["SECRET_KEY"] = "pocketsmart-integration-test-secret"
sys.path.insert(0, str(DEVELOPMENT_DIR))

from fastapi.testclient import TestClient

from app import app


class PocketSmartAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)
        DATABASE_FILE.unlink(missing_ok=True)

    def setUp(self):
        self.client.cookies.clear()
        self.username = f"user_{uuid.uuid4().hex[:12]}"

    def register(self, username=None):
        username = username or self.username
        return self.client.post(
            "/register",
            json={
                "username": username,
                "email": f"{username}@example.test",
                "full_name": "PocketSmart Test User",
                "password": "correct-horse-battery",
            },
        )

    def login(self, username=None, password="correct-horse-battery"):
        return self.client.post(
            "/token",
            data={"username": username or self.username, "password": password},
        )

    def create_account_session(self):
        self.assertEqual(self.register().status_code, 201)
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn("httponly", response.headers["set-cookie"].lower())
        return response

    def test_every_html_template_compiles(self):
        from jinja2 import Environment, FileSystemLoader

        template_dir = DEVELOPMENT_DIR / "templates"
        environment = Environment(loader=FileSystemLoader(str(template_dir)))
        template_files = list(template_dir.glob("*.html"))
        self.assertGreaterEqual(len(template_files), 9)
        for template_file in template_files:
            with self.subTest(template=template_file.name):
                environment.get_template(template_file.name)

    def test_public_pages_static_assets_and_database_startup(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/login").status_code, 200)
        self.assertEqual(self.client.get("/register").status_code, 200)
        self.assertEqual(self.client.get("/static/styles.css").status_code, 200)
        self.assertEqual(self.client.get("/favicon.ico").status_code, 200)
        self.assertEqual(self.client.get("/static/favicon.svg").status_code, 200)
        startup = self.client.get("/startup")
        self.assertEqual(startup.status_code, 200)
        self.assertFalse(startup.json()["ai_enabled"])
        self.assertTrue(DATABASE_FILE.exists())
        self.assertEqual(self.client.get("/dashboard").status_code, 401)
        self.assertEqual(self.client.get("/api/history").status_code, 401)

    def test_gemini_provider_uses_validated_json_when_configured(self):
        from recommendations import generate_recommendations

        valid_response = json.dumps(
            {
                "categories": [
                    {"name": "Room essentials", "allocation": 1000, "items": []}
                ],
                "tips": [],
            }
        )
        client = Mock()
        client.models.generate_content.return_value.text = valid_response
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-provider-key"}):
            with patch("recommendations.genai.Client", return_value=client):
                result, source = generate_recommendations(
                    "home", {"budget": 1000, "rooms": "1", "style": "Modern"}
                )
        self.assertEqual(source, "gemini")
        self.assertEqual(result["categories"][0]["allocation"], 1000)
        client.models.generate_content.assert_called_once()

    def test_registration_password_validation_login_and_logout(self):
        self.assertEqual(self.register().status_code, 201)
        self.assertEqual(self.register().status_code, 409)
        self.assertEqual(
            self.client.post("/register", json={"username": "x", "password": "short"}).status_code,
            422,
        )
        self.assertEqual(
            self.client.post(
                "/register",
                json={"username": "long_password", "password": "a" * 73},
            ).status_code,
            422,
        )
        self.assertEqual(self.login(password="not-the-password").status_code, 401)
        login = self.login()
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.json()["token_type"], "bearer")
        self.assertEqual(self.client.get("/api/me").json()["username"], self.username)
        self.assertEqual(self.client.get("/session-info").json()["username"], self.username)
        self.assertEqual(self.client.get("/session-data").json()["recommendations"], 0)
        self.assertEqual(self.client.get("/dashboard").status_code, 200)
        api_logout = self.client.post("/logout")
        self.assertEqual(api_logout.status_code, 204)
        self.assertEqual(self.client.get("/api/me").status_code, 401)
        self.assertEqual(self.login().status_code, 200)
        response = self.client.get("/logout", follow_redirects=False)
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "/login")
        self.assertEqual(self.client.get("/dashboard").status_code, 401)

    def test_all_planners_fallback_and_history(self):
        self.create_account_session()
        for path in ("/home-planner", "/party-planner", "/jewelry-planner", "/history"):
            self.assertEqual(self.client.get(path).status_code, 200, path)

        plans = [
            (
                "/generate-home",
                {"budget": 50000, "rooms": "2", "style": "Modern", "room_types": ["Living Room"], "platforms": ["IKEA"]},
                "home",
            ),
            (
                "/generate-party",
                {"budget": 30000, "event_type": "Birthday", "guests": "25", "location": "Home", "includes": ["Catering", "Decoration"]},
                "party",
            ),
            (
                "/generate-jewelry",
                {"budget": 12000, "occasion": "Wedding", "jewelry_types": ["Earrings", "Ring"], "platforms": ["Amazon"]},
                "jewelry",
            ),
        ]
        for path, payload, category in plans:
            response = self.client.post(path, json=payload)
            self.assertEqual(response.status_code, 200, response.text)
            body = response.json()
            self.assertEqual(body["source"], "fallback")
            self.assertEqual(body["budget"], payload["budget"])
            import json
            recommendation = json.loads(body["recommendations"])
            if category in {"home", "party"}:
                self.assertEqual(sum(item["allocation"] for item in recommendation["categories"]), payload["budget"])
            else:
                self.assertLessEqual(sum(item["price"] for item in recommendation["jewelry"]), payload["budget"])

        history = self.client.get("/api/history").json()
        self.assertEqual(history["total"], 3)
        self.assertEqual({entry["category"] for entry in history["history"]}, {"home", "party", "jewelry"})
        cleared = self.client.delete("/api/history")
        self.assertEqual(cleared.status_code, 200)
        self.assertEqual(cleared.json()["deleted"], 3)
        self.assertEqual(self.client.get("/api/history").json()["total"], 0)

    def test_history_is_isolated_between_accounts_and_bearer_auth_works(self):
        self.create_account_session()
        response = self.client.post(
            "/generate-home",
            json={"budget": 1000, "rooms": "1", "style": "Modern"},
        )
        self.assertEqual(response.status_code, 200)
        other_username = f"other_{uuid.uuid4().hex[:12]}"
        self.assertEqual(self.register(other_username).status_code, 201)
        bearer_login = self.login(other_username)
        bearer_token = bearer_login.json()["access_token"]
        self.client.cookies.clear()
        self.client.headers.update({"Authorization": f"Bearer {bearer_token}"})
        self.assertEqual(self.client.get("/api/history").json()["total"], 0)
        self.client.headers.pop("Authorization", None)

    def test_party_plan_without_selected_services_still_uses_full_budget(self):
        self.create_account_session()
        response = self.client.post(
            "/generate-party",
            json={
                "budget": 25000,
                "event_type": "Birthday",
                "guests": 20,
                "includes": [],
            },
        )
        self.assertEqual(response.status_code, 200)
        result = __import__("json").loads(response.json()["recommendations"])
        self.assertEqual(
            sum(category["allocation"] for category in result["categories"]),
            25000,
        )

    def test_invalid_planner_inputs_and_outfit_images(self):
        self.create_account_session()
        self.assertEqual(
            self.client.post("/generate-home", json={"budget": 0, "rooms": "1", "style": "Modern"}).status_code,
            422,
        )
        self.assertEqual(
            self.client.post("/generate-party", json={"budget": 1000, "event_type": "Birthday", "guests": 0}).status_code,
            422,
        )
        self.assertEqual(
            self.client.post(
                "/generate-jewelry",
                json={"budget": 1000, "occasion": "Wedding", "image": "not-base64"},
            ).status_code,
            422,
        )
        from PIL import Image

        image_buffer = io.BytesIO()
        Image.new("RGB", (4, 4), color=(25, 80, 140)).save(image_buffer, format="PNG")
        encoded_image = base64.b64encode(image_buffer.getvalue()).decode("ascii")
        image_response = self.client.post(
            "/generate-jewelry",
            json={
                "budget": 3000,
                "occasion": "Wedding",
                "jewelry_types": ["Earrings"],
                "image": encoded_image,
            },
        )
        self.assertEqual(image_response.status_code, 200, image_response.text)
        self.assertEqual(image_response.json()["source"], "fallback")
        image_plan = __import__("json").loads(image_response.json()["recommendations"])
        self.assertIsNone(image_plan["outfit_analysis"])
        self.assertTrue(any("unavailable in offline mode" in tip for tip in image_plan["tips"]))
        generic = self.client.post(
            "/recommendations-details",
            json={"category": "home", "budget": 1000, "preferences": {"rooms": "1"}},
        )
        self.assertEqual(generic.status_code, 200)
        self.assertEqual(generic.json()["source"], "fallback")
        self.assertEqual(self.client.get("/session-info").status_code, 200)


if __name__ == "__main__":
    unittest.main()
