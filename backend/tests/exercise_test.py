from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_create_exercise():
    response = client.post(
        "/exercises/",
        json={
            "name": "Bench Press",
            "category": "Compound",
            "primary_muscle": "Chest",
            "equipment": "Barbell",
            "description": "Flat barbell bench press",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Bench Press"
    assert data["category"] == "Compound"
    assert data["primary_muscle"] == "Chest"
    assert data["equipment"] == "Barbell"
    assert data["description"] == "Flat barbell bench press"
    assert "id" in data