from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def unique_exercise_name(base: str = "Bench Press") -> str:
    return f"{base} {uuid4().hex}"


def create_test_exercise(
    name: str | None = None,
    category: str = "Strength",
    primary_muscle: str = "Chest",
    equipment: str = "Barbell",
    description: str = "Test exercise",
):
    exercise_name = name or unique_exercise_name()

    response = client.post(
        "/exercises/",
        json={
            "name": exercise_name,
            "category": category,
            "primary_muscle": primary_muscle,
            "equipment": equipment,
            "description": description,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_exercise():
    exercise_name = unique_exercise_name()

    response = client.post(
        "/exercises/",
        json={
            "name": exercise_name,
            "category": "Strength",
            "primary_muscle": "Chest",
            "equipment": "Barbell",
            "description": "Flat barbell bench press",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == exercise_name
    assert data["category"] == "Strength"
    assert data["primary_muscle"] == "Chest"
    assert data["equipment"] == "Barbell"
    assert data["description"] == "Flat barbell bench press"
    assert "id" in data


def test_list_exercises():
    exercise = create_test_exercise(base_name := unique_exercise_name("Squat"))

    response = client.get("/exercises/")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert any(item["id"] == exercise["id"] for item in data)
    assert any(item["name"] == base_name for item in data)


def test_list_exercises_with_search():
    exercise_name = unique_exercise_name("Searchable Bench")
    create_test_exercise(name=exercise_name)

    response = client.get(f"/exercises/?search={exercise_name}")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(item["name"] == exercise_name for item in data)


def test_get_exercise():
    exercise = create_test_exercise()

    response = client.get(f"/exercises/{exercise['id']}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == exercise["id"]
    assert data["name"] == exercise["name"]
    assert data["category"] == exercise["category"]


def test_get_exercise_not_found():
    response = client.get("/exercises/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise not found"


def test_update_exercise():
    exercise = create_test_exercise(
        name=unique_exercise_name("Old Exercise"),
        description="Old description",
    )

    response = client.patch(
        f"/exercises/{exercise['id']}",
        json={
            "name": unique_exercise_name("Updated Exercise"),
            "description": "Updated description",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == exercise["id"]
    assert data["name"].startswith("Updated Exercise")
    assert data["description"] == "Updated description"


def test_update_exercise_partial_keeps_existing_fields():
    exercise = create_test_exercise(
        category="Strength",
        primary_muscle="Back",
        equipment="Bodyweight",
        description="Original description",
    )

    response = client.patch(
        f"/exercises/{exercise['id']}",
        json={
            "description": "Only description changed",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == exercise["id"]
    assert data["name"] == exercise["name"]
    assert data["category"] == "Strength"
    assert data["primary_muscle"] == "Back"
    assert data["equipment"] == "Bodyweight"
    assert data["description"] == "Only description changed"


def test_update_exercise_not_found():
    response = client.patch(
        "/exercises/999999",
        json={
            "name": unique_exercise_name("Does Not Exist"),
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise not found"


def test_delete_exercise():
    exercise = create_test_exercise(name=unique_exercise_name("Delete Me"))

    delete_response = client.delete(f"/exercises/{exercise['id']}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/exercises/{exercise['id']}")

    assert get_response.status_code == 404


def test_delete_exercise_not_found():
    response = client.delete("/exercises/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise not found"


def test_create_duplicate_exercise_returns_409():
    exercise_name = unique_exercise_name("Duplicate Exercise")

    create_test_exercise(name=exercise_name)

    response = client.post(
        "/exercises/",
        json={
            "name": exercise_name,
            "category": "Strength",
            "primary_muscle": "Chest",
            "equipment": "Barbell",
            "description": "Duplicate attempt",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "An exercise with this name already exists."