from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_test_program(
    name: str | None = None,
    description: str = "Test program description",
):
    program_name = name or f"Test Program {uuid4().hex}"

    response = client.post(
        "/programs/",
        json={
            "name": program_name,
            "description": description,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_program(override_current_user):
    user = override_current_user

    response = client.post(
        "/programs/",
        json={
            "name": f"Powerlifting Block {uuid4().hex}",
            "description": "Bench-focused strength block",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["user_id"] == user.id
    assert data["name"].startswith("Powerlifting Block")
    assert data["description"] == "Bench-focused strength block"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_list_programs(override_current_user):
    program = create_test_program(
        name=f"Hypertrophy Block {uuid4().hex}",
        description="Volume-focused block",
    )

    response = client.get("/programs/")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert any(item["id"] == program["id"] for item in data)
    assert any(item["name"] == program["name"] for item in data)


def test_list_programs_with_search(override_current_user):
    program_name = f"Searchable Bench Program {uuid4().hex}"

    create_test_program(
        name=program_name,
        description="Search test program",
    )

    response = client.get(f"/programs/?search={program_name}")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(item["name"] == program_name for item in data)


def test_get_program(override_current_user):
    user = override_current_user

    program = create_test_program(
        name=f"Strength Block {uuid4().hex}",
        description="General strength block",
    )

    response = client.get(f"/programs/{program['id']}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == program["id"]
    assert data["name"] == program["name"]
    assert data["user_id"] == user.id
    assert data["description"] == "General strength block"


def test_get_program_not_found(override_current_user):
    response = client.get("/programs/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"


def test_update_program(override_current_user):
    user = override_current_user

    program = create_test_program(
        name=f"Old Program Name {uuid4().hex}",
        description="Old description",
    )

    response = client.patch(
        f"/programs/{program['id']}",
        json={
            "name": f"Updated Program Name {uuid4().hex}",
            "description": "Updated description",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == program["id"]
    assert data["name"].startswith("Updated Program Name")
    assert data["description"] == "Updated description"
    assert data["user_id"] == user.id


def test_update_program_partial_keeps_existing_fields(override_current_user):
    user = override_current_user

    program = create_test_program(
        name=f"Partial Update Program {uuid4().hex}",
        description="Original description",
    )

    response = client.patch(
        f"/programs/{program['id']}",
        json={
            "description": "Only description changed",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == program["id"]
    assert data["name"] == program["name"]
    assert data["description"] == "Only description changed"
    assert data["user_id"] == user.id


def test_update_program_not_found(override_current_user):
    response = client.patch(
        "/programs/999999",
        json={
            "name": f"Does Not Exist {uuid4().hex}",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"


def test_delete_program(override_current_user):
    program = create_test_program(
        name=f"Program To Delete {uuid4().hex}",
        description="This should be deleted",
    )

    delete_response = client.delete(f"/programs/{program['id']}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/programs/{program['id']}")

    assert get_response.status_code == 404


def test_delete_program_not_found(override_current_user):
    response = client.delete("/programs/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"


def test_create_program_without_auth_returns_401():
    response = client.post(
        "/programs/",
        json={
            "name": f"Unauthenticated Program {uuid4().hex}",
            "description": "This should fail without auth",
        },
    )

    assert response.status_code == 401