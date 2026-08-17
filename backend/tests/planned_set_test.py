from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_test_program():
    response = client.post(
        "/programs/",
        json={
            "name": f"Planned Set Test Program {uuid4().hex}",
            "description": "Program used for planned set tests",
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
):
    response = client.post(
        f"/program-weeks/{week_id}/days",
        json={
            "name": name,
            "day_order": day_order,
            "notes": "Test workout day",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_exercise(name: str | None = None):
    exercise_name = name or f"Test Exercise {uuid4().hex}"

    response = client.post(
        "/exercises/",
        json={
            "name": exercise_name,
            "category": "Strength",
            "primary_muscle": "Chest",
            "equipment": "Barbell",
            "description": "Test exercise for planned set tests",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_workout_exercise(
    day_id: int,
    exercise_id: int,
    exercise_order: int = 1,
):
    response = client.post(
        f"/workout-days/{day_id}/exercises",
        json={
            "exercise_id": exercise_id,
            "exercise_order": exercise_order,
            "notes": "Test workout exercise",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_planned_set(
    workout_exercise_id: int,
    set_order: int = 1,
    target_reps: int = 5,
    target_weight: float | None = 225.0,
    target_rpe: float | None = 7.0,
    notes: str | None = "Test planned set",
):
    response = client.post(
        f"/workout-exercises/{workout_exercise_id}/sets",
        json={
            "set_order": set_order,
            "target_reps": target_reps,
            "target_weight": target_weight,
            "target_rpe": target_rpe,
            "notes": notes,
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_planned_set_setup(user):
    program = create_test_program()
    week = create_test_program_week(program["id"])
    day = create_test_workout_day(week["id"])
    exercise = create_test_exercise()
    workout_exercise = create_test_workout_exercise(
        day_id=day["id"],
        exercise_id=exercise["id"],
    )

    return {
        "user": user,
        "program": program,
        "week": week,
        "day": day,
        "exercise": exercise,
        "workout_exercise": workout_exercise,
    }


def test_create_planned_set(override_current_user):
    setup = create_test_planned_set_setup(override_current_user)

    response = client.post(
        f"/workout-exercises/{setup['workout_exercise']['id']}/sets",
        json={
            "set_order": 1,
            "target_reps": 5,
            "target_weight": 225.0,
            "target_rpe": 7.0,
            "notes": "Pause all reps",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["workout_exercise_id"] == setup["workout_exercise"]["id"]
    assert data["set_order"] == 1
    assert data["target_reps"] == 5
    assert data["target_weight"] == 225.0
    assert data["target_rpe"] == 7.0
    assert data["notes"] == "Pause all reps"


def test_create_planned_set_with_missing_workout_exercise_returns_404(override_current_user):
    response = client.post(
        "/workout-exercises/999999/sets",
        json={
            "set_order": 1,
            "target_reps": 5,
            "target_weight": 225.0,
            "target_rpe": 7.0,
            "notes": "Invalid parent workout exercise",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout exercise not found"


def test_list_planned_sets(override_current_user):
    setup = create_test_planned_set_setup(override_current_user)

    set_1 = create_test_planned_set(
        workout_exercise_id=setup["workout_exercise"]["id"],
        set_order=1,
        target_reps=5,
    )

    set_2 = create_test_planned_set(
        workout_exercise_id=setup["workout_exercise"]["id"],
        set_order=2,
        target_reps=5,
    )

    response = client.get(
        f"/workout-exercises/{setup['workout_exercise']['id']}/sets"
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    planned_set_ids = [item["id"] for item in data]

    assert set_1["id"] in planned_set_ids
    assert set_2["id"] in planned_set_ids


def test_list_planned_sets_only_returns_sets_for_that_workout_exercise(override_current_user):
    setup = create_test_planned_set_setup(override_current_user)

    exercise_2 = create_test_exercise(name=f"Second Exercise {uuid4().hex}")
    workout_exercise_2 = create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=exercise_2["id"],
        exercise_order=2,
    )

    set_1 = create_test_planned_set(
        workout_exercise_id=setup["workout_exercise"]["id"],
        set_order=1,
    )

    set_2 = create_test_planned_set(
        workout_exercise_id=workout_exercise_2["id"],
        set_order=1,
    )

    response = client.get(
        f"/workout-exercises/{setup['workout_exercise']['id']}/sets"
    )

    assert response.status_code == 200

    data = response.json()
    planned_set_ids = [item["id"] for item in data]

    assert set_1["id"] in planned_set_ids
    assert set_2["id"] not in planned_set_ids


def test_list_planned_sets_orders_by_set_order(override_current_user):
    setup = create_test_planned_set_setup(override_current_user)

    create_test_planned_set(
        workout_exercise_id=setup["workout_exercise"]["id"],
        set_order=3,
    )

    create_test_planned_set(
        workout_exercise_id=setup["workout_exercise"]["id"],
        set_order=1,
    )

    create_test_planned_set(
        workout_exercise_id=setup["workout_exercise"]["id"],
        set_order=2,
    )

    response = client.get(
        f"/workout-exercises/{setup['workout_exercise']['id']}/sets"
    )

    assert response.status_code == 200

    data = response.json()
    set_orders = [item["set_order"] for item in data]

    assert set_orders == sorted(set_orders)