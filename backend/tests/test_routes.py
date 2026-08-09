import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch

groq_stub = types.ModuleType("groq")
groq_stub.Groq = object
sys.modules.setdefault("groq", groq_stub)

supabase_stub = types.ModuleType("supabase")
supabase_stub.Client = object
supabase_stub.create_client = lambda *args, **kwargs: None
sys.modules.setdefault("supabase", supabase_stub)

slowapi_stub = types.ModuleType("slowapi")


class DummyLimiter:
    def __init__(self, *args, **kwargs):
        pass

    def limit(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator


slowapi_stub.Limiter = DummyLimiter
slowapi_stub._rate_limit_exceeded_handler = lambda *args, **kwargs: None
sys.modules.setdefault("slowapi", slowapi_stub)

slowapi_errors_stub = types.ModuleType("slowapi.errors")
slowapi_errors_stub.RateLimitExceeded = Exception
sys.modules.setdefault("slowapi.errors", slowapi_errors_stub)

slowapi_util_stub = types.ModuleType("slowapi.util")
slowapi_util_stub.get_remote_address = lambda request: "127.0.0.1"
sys.modules.setdefault("slowapi.util", slowapi_util_stub)

from fastapi.testclient import TestClient

from app.dependencies.auth import get_current_user
from app.main import create_app


TEST_USER = SimpleNamespace(id="test-user-123", email="test@example.com")


class AuthBypassRouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.dependency_overrides[get_current_user] = lambda: TEST_USER
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides.clear()

    @patch("app.routers.roadmaps.roadmap_repository.list_roadmaps")
    def test_get_roadmaps_with_auth_override(self, mock_list_roadmaps):
        mock_list_roadmaps.return_value = [
            {"id": "roadmap-1", "title": "Test roadmap"},
        ]

        response = self.client.get("/roadmaps")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"roadmaps": [{"id": "roadmap-1", "title": "Test roadmap"}]},
        )
        mock_list_roadmaps.assert_called_once_with("test-user-123")

    @patch("app.routers.essays.generate_and_store_essay_feedback")
    def test_post_essay_with_auth_override(self, mock_generate_essay):
        mock_generate_essay.return_value = {
            "feedback": {"letter_grade": 88, "summary_badge": "Strong"},
            "id": "essay-1",
        }

        payload = {
            "grade": "11",
            "prompt": "Describe a challenge you've overcome.",
            "essay": "I learned how to ask for help and grow from failure.",
            "program": "Computer Science",
            "word_limit": 650,
        }

        response = self.client.post("/essay", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "feedback": {"letter_grade": 88, "summary_badge": "Strong"},
                "id": "essay-1",
                "warning": None,
            },
        )

        mock_generate_essay.assert_called_once()
        request_payload, user_id = mock_generate_essay.call_args.args
        self.assertEqual(request_payload.grade, "11")
        self.assertEqual(request_payload.program, "Computer Science")
        self.assertEqual(user_id, "test-user-123")


if __name__ == "__main__":
    unittest.main()
