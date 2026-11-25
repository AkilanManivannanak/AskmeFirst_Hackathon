"""Server endpoints that must work with no API keys and no network."""
import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_health_is_up():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_security_headers_are_set():
    h = client.get("/api/health").headers
    assert h["X-Frame-Options"] == "DENY"
    assert h["X-Content-Type-Options"] == "nosniff"
    assert h["Referrer-Policy"] == "no-referrer"


def test_static_only_serves_whitelisted_files():
    assert client.get("/static/gsap.min.js").status_code == 200
    assert client.get("/static/.env").status_code == 404
    assert client.get("/static/main.py").status_code == 404


def test_voice_check_skips_short_text():
    r = client.post("/api/voice_check", json={"text": "too short to check"})
    assert r.json() == {"eligible": False, "words": 4}


@pytest.fixture
def tight_limit(monkeypatch):
    monkeypatch.setattr(main, "RATE_LIMIT", 2)
    main._RATE.clear()
    yield
    main._RATE.clear()


def test_rate_limit_blocks_extra_posts(tight_limit):
    codes = [client.post("/api/voice_check", json={"text": "hi"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]
