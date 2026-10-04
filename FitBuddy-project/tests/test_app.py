import os
import tempfile
from pathlib import Path

DB_FILE = Path(tempfile.gettempdir()) / "fitbuddy_test.sqlite"
if DB_FILE.exists(): DB_FILE.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{DB_FILE}"
os.environ["ALLOW_AI_FALLBACK"] = "true"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

from app.database import init_db
init_db()

def test_home():
    r = client.get("/")
    assert r.status_code == 200
    assert "FitBuddy" in r.text

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_generate_without_api_key():
    r = client.post("/api/generate-workout", json={
        "name":"Test User","user_id":"TEST001","age":20,"weight":60,
        "goal":"general wellness","intensity":"medium"
    })
    assert r.status_code == 200
    body = r.json()
    assert body["plan_id"]
    assert "Day 1" in body["workout_plan"]
    assert body["nutrition_tip"]

def test_feedback():
    r = client.post("/api/submit-feedback", json={"user_id":"TEST001","feedback":"Add more cardio."})
    assert r.status_code == 200
    assert "UPDATED USING FEEDBACK" in r.json()["updated_plan"]
