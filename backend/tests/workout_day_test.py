from uuid import uuid4

from fastapi.testclient import TestClient

from tests.test_database import TestingSessionLocal
from app.main import app
from app.models import User

client = TestClient(app)


def create_test_user() -> User:
    db = TestingSessionLocal()

    try:
        unique_id = uuid4().hex

        user = User(
            email=f"workoutdaytest_{unique_id}@example.com",
            username=f"workoutdaytestuser_{unique_id}",
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
            "name": f"Workout Day Test Program {uuid4().hex}",
            "description": "Program used for workout day tests",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_program_week(program_id: int, week_number: int = 1):
    response = client.post(
        f"/programs/{program_id}/weeks",
        json={
            "week_number": week_number,
            "notes": "Test program week",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_workout_day(
    week_id: int,
    name: str = "Upper Day",
    day_order: int = 1,
    notes: str | None = "Test workout day",
):
    response = client.post(
        f"/program-weeks/{week_id}/days",
        json={
            "name": name,
            "day_order": day_order,
            "notes": notes,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_workout_day():
    user = create_test_user()
    program = create_test_program(user.id)
    week = create_test_program_week(program["id"])

    response = client.post(
        f"/program-weeks/{week['id']}/days",
        json={
            "name": "Upper 1",
            "day_order": 1,
            "notes": "Bench-focused day",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["program_week_id"] == week["id"]
    assert data["name"] == "Upper 1"
    assert data["day_order"] == 1
    assert data["notes"] == "Bench-focused day"


def test_create_workout_day_with_missing_week_returns_404():
    response = client.post(
        "/program-weeks/999999/days",
        json={
            "name": "Invalid Day",
            "day_order": 1,
            "notes": "Parent week does not exist",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Program week not found"


def test_list_workout_days():
    user = create_test_user()
    program = create_test_program(user.id)
    week = create_test_program_week(program["id"])

    day_1 = create_test_workout_day(
        week_id=week["id"],
        name="Upper 1",
        day_order=1,
    )

    day_2 = create_test_workout_day(
        week_id=week["id"],
        name="Lower 1",
        day_order=2,
    )

    response = client.get(f"/program-weeks/{week['id']}/days")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    day_ids = [day["id"] for day in data]

    assert day_1["id"] in day_ids
    assert day_2["id"] in day_ids


def test_list_workout_days_only_returns_days_for_that_week():
    user = create_test_user()
    program = create_test_program(user.id)

    week_1 = create_test_program_week(program["id"], week_number=1)
    week_2 = create_test_program_week(program["id"], week_number=2)

    week_1_day = create_test_workout_day(
        week_id=week_1["id"],
        name="Week 1 Upper",
        day_order=1,
    )

    week_2_day = create_test_workout_day(
        week_id=week_2["id"],
        name="Week 2 Upper",
        day_order=1,
    )

    response = client.get(f"/program-weeks/{week_1['id']}/days")

    assert response.status_code == 200

    data = response.json()
    day_ids = [day["id"] for day in data]

    assert week_1_day["id"] in day_ids
    assert week_2_day["id"] not in day_ids


def test_list_workout_days_orders_by_day_order():
    user = create_test_user()
    program = create_test_program(user.id)
    week = create_test_program_week(program["id"])

    create_test_workout_day(
        week_id=week["id"],
        name="Day 3",
        day_order=3,
    )

    create_test_workout_day(
        week_id=week["id"],
        name="Day 1",
        day_order=1,
    )

    create_test_workout_day(
        week_id=week["id"],
        name="Day 2",
        day_order=2,
    )

    response = client.get(f"/program-weeks/{week['id']}/days")

    assert response.status_code == 200

    data = response.json()
    day_orders = [day["day_order"] for day in data]

    assert day_orders == sorted(day_orders)


def test_list_workout_days_with_missing_week_returns_404():
    response = client.get("/program-weeks/999999/days")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program week not found"


def test_get_workout_day():
    user = create_test_user()
    program = create_test_program(user.id)
    week = create_test_program_week(program["id"])

    day = create_test_workout_day(
        week_id=week["id"],
        name="Upper 2",
        day_order=2,
        notes="Day to get",
    )

    response = client.get(f"/workout-days/{day['id']}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == day["id"]
    assert data["program_week_id"] == week["id"]
    assert data["name"] == "Upper 2"
    assert data["day_order"] == 2
    assert data["notes"] == "Day to get"


def test_get_workout_day_not_found():
    response = client.get("/workout-days/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout day not found"


def test_update_workout_day():
    user = create_test_user()
    program = create_test_program(user.id)
    week = create_test_program_week(program["id"])

    day = create_test_workout_day(
        week_id=week["id"],
        name="Old Day Name",
        day_order=1,
        notes="Old notes",
    )

    response = client.patch(
        f"/workout-days/{day['id']}",
        json={
            "name": "Updated Day Name",
            "day_order": 2,
            "notes": "Updated notes",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == day["id"]
    assert data["program_week_id"] == week["id"]
    assert data["name"] == "Updated Day Name"
    assert data["day_order"] == 2
    assert data["notes"] == "Updated notes"


def test_update_workout_day_partial_keeps_existing_fields():
    user = create_test_user()
    program = create_test_program(user.id)
    week = create_test_program_week(program["id"])

    day = create_test_workout_day(
        week_id=week["id"],
        name="Upper Day",
        day_order=1,
        notes="Original notes",
    )

    response = client.patch(
        f"/workout-days/{day['id']}",
        json={
            "notes": "Only notes changed",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == day["id"]
    assert data["program_week_id"] == week["id"]
    assert data["name"] == "Upper Day"
    assert data["day_order"] == 1
    assert data["notes"] == "Only notes changed"


def test_update_workout_day_not_found():
    response = client.patch(
        "/workout-days/999999",
        json={
            "name": "Does Not Exist",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout day not found"


def test_delete_workout_day():
    user = create_test_user()
    program = create_test_program(user.id)
    week = create_test_program_week(program["id"])

    day = create_test_workout_day(
        week_id=week["id"],
        name="Day To Delete",
        day_order=1,
    )

    delete_response = client.delete(f"/workout-days/{day['id']}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/workout-days/{day['id']}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Workout day not found"


def test_delete_workout_day_not_found():
    response = client.delete("/workout-days/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout day not found"