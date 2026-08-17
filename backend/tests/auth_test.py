from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.dependencies.auth_dependencies import get_current_user
from app.main import app
from app.models import User
from tests.test_database import TestingSessionLocal

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_auth_override():
    app.dependency_overrides.pop(get_current_user, None)

    yield

    app.dependency_overrides.pop(get_current_user, None)


def create_test_user(prefix: str = "authztest") -> User:
    db = TestingSessionLocal()

    try:
        unique_id = uuid4().hex

        user = User(
            email=f"{prefix}_{unique_id}@example.com",
            username=f"{prefix}_{unique_id}",
            password_hash="fake_hashed_password",
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)

        return user

    finally:
        db.close()


def authenticate_as(user: User):
    def _override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = _override_get_current_user


def create_test_program():
    response = client.post(
        "/programs/",
        json={
            "name": f"Authorization Test Program {uuid4().hex}",
            "description": "Program used for authorization tests",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_program_week(program_id: int):
    response = client.post(
        f"/programs/{program_id}/weeks",
        json={
            "week_number": 1,
            "notes": "Authorization test week",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_workout_day(week_id: int):
    response = client.post(
        f"/program-weeks/{week_id}/days",
        json={
            "name": "Authorization Test Day",
            "day_order": 1,
            "notes": "Authorization test day",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_exercise():
    response = client.post(
        "/exercises/",
        json={
            "name": f"Authorization Test Exercise {uuid4().hex}",
            "category": "Strength",
            "primary_muscle": "Chest",
            "equipment": "Barbell",
            "description": "Authorization test exercise",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_workout_exercise(day_id: int, exercise_id: int):
    response = client.post(
        f"/workout-days/{day_id}/exercises",
        json={
            "exercise_id": exercise_id,
            "exercise_order": 1,
            "notes": "Authorization test workout exercise",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_planned_set(workout_exercise_id: int):
    response = client.post(
        f"/workout-exercises/{workout_exercise_id}/sets",
        json={
            "set_order": 1,
            "target_reps": 5,
            "target_weight": 225.0,
            "target_rpe": 7.0,
            "notes": "Authorization test planned set",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_full_program_setup(owner: User):
    authenticate_as(owner)

    program = create_test_program()
    week = create_test_program_week(program["id"])
    day = create_test_workout_day(week["id"])
    exercise = create_test_exercise()
    workout_exercise = create_test_workout_exercise(day["id"], exercise["id"])
    planned_set = create_test_planned_set(workout_exercise["id"])

    return {
        "program": program,
        "week": week,
        "day": day,
        "exercise": exercise,
        "workout_exercise": workout_exercise,
        "planned_set": planned_set,
    }


def test_user_cannot_get_another_users_program():
    owner = create_test_user("owner")
    other_user = create_test_user("other")

    setup = create_full_program_setup(owner)

    authenticate_as(other_user)

    response = client.get(f"/programs/{setup['program']['id']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"


def test_user_cannot_get_another_users_program_detail():
    owner = create_test_user("owner")
    other_user = create_test_user("other")

    setup = create_full_program_setup(owner)

    authenticate_as(other_user)

    response = client.get(f"/programs/{setup['program']['id']}/detail")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"


def test_user_cannot_create_week_under_another_users_program():
    owner = create_test_user("owner")
    other_user = create_test_user("other")

    setup = create_full_program_setup(owner)

    authenticate_as(other_user)

    response = client.post(
        f"/programs/{setup['program']['id']}/weeks",
        json={
            "week_number": 2,
            "notes": "Should not be allowed",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"


def test_user_cannot_get_another_users_program_week():
    owner = create_test_user("owner")
    other_user = create_test_user("other")

    setup = create_full_program_setup(owner)

    authenticate_as(other_user)

    response = client.get(f"/program-weeks/{setup['week']['id']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program week not found"


def test_user_cannot_create_day_under_another_users_week():
    owner = create_test_user("owner")
    other_user = create_test_user("other")

    setup = create_full_program_setup(owner)

    authenticate_as(other_user)

    response = client.post(
        f"/program-weeks/{setup['week']['id']}/days",
        json={
            "name": "Unauthorized Day",
            "day_order": 2,
            "notes": "Should not be allowed",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Program week not found"


def test_user_cannot_get_another_users_workout_day():
    owner = create_test_user("owner")
    other_user = create_test_user("other")

    setup = create_full_program_setup(owner)

    authenticate_as(other_user)

    response = client.get(f"/workout-days/{setup['day']['id']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout day not found"


def test_user_cannot_create_workout_exercise_under_another_users_day():
    owner = create_test_user("owner")
    other_user = create_test_user("other")

    setup = create_full_program_setup(owner)

    authenticate_as(other_user)

    response = client.post(
        f"/workout-days/{setup['day']['id']}/exercises",
        json={
            "exercise_id": setup["exercise"]["id"],
            "exercise_order": 2,
            "notes": "Should not be allowed",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout day not found"


def test_user_cannot_get_another_users_workout_exercise():
    owner = create_test_user("owner")
    other_user = create_test_user("other")

    setup = create_full_program_setup(owner)

    authenticate_as(other_user)

    response = client.get(f"/workout-exercises/{setup['workout_exercise']['id']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout exercise not found"


def test_user_cannot_create_planned_set_under_another_users_workout_exercise():
    owner = create_test_user("owner")
    other_user = create_test_user("other")

    setup = create_full_program_setup(owner)

    authenticate_as(other_user)

    response = client.post(
        f"/workout-exercises/{setup['workout_exercise']['id']}/sets",
        json={
            "set_order": 2,
            "target_reps": 8,
            "target_weight": 185.0,
            "target_rpe": 6.0,
            "notes": "Should not be allowed",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout exercise not found"


def test_user_cannot_get_another_users_planned_set():
    owner = create_test_user("owner")
    other_user = create_test_user("other")

    setup = create_full_program_setup(owner)

    authenticate_as(other_user)

    response = client.get(f"/planned-sets/{setup['planned_set']['id']}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Planned set not found"