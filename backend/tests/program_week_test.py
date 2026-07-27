from uuid import uuid4

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import User

client = TestClient(app)


def create_test_user() -> User:
    db = SessionLocal()

    try:
        unique_id = uuid4().hex

        user = User(
            email=f"programweektest_{unique_id}@example.com",
            username=f"programweektestuser_{unique_id}",
            password_hash="fake_hashed_password",
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)

        return user

    finally:
        db.close()


def create_test_program(user_id: int):
    response = client.post(
        "/programs/",
        json={
            "user_id": user_id,
            "name": f"Program Week Test Program {uuid4().hex}",
            "description": "Program used for program week tests",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_program_week(
    program_id: int,
    week_number: int = 1,
    notes: str | None = "Test program week",
):
    response = client.post(
        f"/programs/{program_id}/weeks",
        json={
            "week_number": week_number,
            "notes": notes,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_program_week():
    user = create_test_user()
    program = create_test_program(user.id)

    response = client.post(
        f"/programs/{program['id']}/weeks",
        json={
            "week_number": 1,
            "notes": "Intro accumulation week",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["program_id"] == program["id"]
    assert data["week_number"] == 1
    assert data["notes"] == "Intro accumulation week"


def test_create_program_week_with_missing_program_returns_404():
    response = client.post(
        "/programs/999999/weeks",
        json={
            "week_number": 1,
            "notes": "Invalid parent program",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"


def test_list_program_weeks():
    user = create_test_user()
    program = create_test_program(user.id)

    week_1 = create_test_program_week(
        program_id=program["id"],
        week_number=1,
        notes="Week 1",
    )

    week_2 = create_test_program_week(
        program_id=program["id"],
        week_number=2,
        notes="Week 2",
    )

    response = client.get(f"/programs/{program['id']}/weeks")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    week_ids = [week["id"] for week in data]

    assert week_1["id"] in week_ids
    assert week_2["id"] in week_ids


def test_list_program_weeks_only_returns_weeks_for_that_program():
    user = create_test_user()

    program_1 = create_test_program(user.id)
    program_2 = create_test_program(user.id)

    program_1_week = create_test_program_week(
        program_id=program_1["id"],
        week_number=1,
        notes="Program 1 week",
    )

    program_2_week = create_test_program_week(
        program_id=program_2["id"],
        week_number=1,
        notes="Program 2 week",
    )

    response = client.get(f"/programs/{program_1['id']}/weeks")

    assert response.status_code == 200

    data = response.json()
    week_ids = [week["id"] for week in data]

    assert program_1_week["id"] in week_ids
    assert program_2_week["id"] not in week_ids


def test_list_program_weeks_orders_by_week_number():
    user = create_test_user()
    program = create_test_program(user.id)

    create_test_program_week(
        program_id=program["id"],
        week_number=3,
        notes="Week 3",
    )

    create_test_program_week(
        program_id=program["id"],
        week_number=1,
        notes="Week 1",
    )

    create_test_program_week(
        program_id=program["id"],
        week_number=2,
        notes="Week 2",
    )

    response = client.get(f"/programs/{program['id']}/weeks")

    assert response.status_code == 200

    data = response.json()
    week_numbers = [week["week_number"] for week in data]

    assert week_numbers == sorted(week_numbers)


def test_list_program_weeks_with_missing_program_returns_404():
    response = client.get("/programs/999999/weeks")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"


def test_get_program_week():
    user = create_test_user()
    program = create_test_program(user.id)

    week = create_test_program_week(
        program_id=program["id"],
        week_number=2,
        notes="Week to get",
    )

    response = client.get(f"/program-weeks/{week['id']}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == week["id"]
    assert data["program_id"] == program["id"]
    assert data["week_number"] == 2
    assert data["notes"] == "Week to get"


def test_get_program_week_not_found():
    response = client.get("/program-weeks/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program week not found"


def test_update_program_week():
    user = create_test_user()
    program = create_test_program(user.id)

    week = create_test_program_week(
        program_id=program["id"],
        week_number=1,
        notes="Old notes",
    )

    response = client.patch(
        f"/program-weeks/{week['id']}",
        json={
            "week_number": 2,
            "notes": "Updated notes",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == week["id"]
    assert data["program_id"] == program["id"]
    assert data["week_number"] == 2
    assert data["notes"] == "Updated notes"


def test_update_program_week_partial_keeps_existing_fields():
    user = create_test_user()
    program = create_test_program(user.id)

    week = create_test_program_week(
        program_id=program["id"],
        week_number=3,
        notes="Original notes",
    )

    response = client.patch(
        f"/program-weeks/{week['id']}",
        json={
            "notes": "Only notes changed",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == week["id"]
    assert data["program_id"] == program["id"]
    assert data["week_number"] == 3
    assert data["notes"] == "Only notes changed"


def test_update_program_week_not_found():
    response = client.patch(
        "/program-weeks/999999",
        json={
            "notes": "Does not exist",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Program week not found"


def test_delete_program_week():
    user = create_test_user()
    program = create_test_program(user.id)

    week = create_test_program_week(
        program_id=program["id"],
        week_number=4,
        notes="Week to delete",
    )

    delete_response = client.delete(f"/program-weeks/{week['id']}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/program-weeks/{week['id']}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Program week not found"


def test_delete_program_week_not_found():
    response = client.delete("/program-weeks/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program week not found"