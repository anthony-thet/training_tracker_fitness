from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_test_program():
    response = client.post(
        "/programs/",
        json={
            "name": f"Workout Exercise Test Program {uuid4().hex}",
            "description": "Program used for workout exercise tests",
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
            "description": "Test exercise for workout exercise tests",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_workout_exercise(
    day_id: int,
    exercise_id: int,
    exercise_order: int = 1,
    notes: str | None = "Test workout exercise",
):
    response = client.post(
        f"/workout-days/{day_id}/exercises",
        json={
            "exercise_id": exercise_id,
            "exercise_order": exercise_order,
            "notes": notes,
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_workout_day_setup():
    program = create_test_program()
    week = create_test_program_week(program["id"])
    day = create_test_workout_day(week["id"])

    return {
        "program": program,
        "week": week,
        "day": day,
    }


def test_create_workout_exercise(override_current_user):
    setup = create_test_workout_day_setup()
    exercise = create_test_exercise(name=f"Bench Press {uuid4().hex}")

    response = client.post(
        f"/workout-days/{setup['day']['id']}/exercises",
        json={
            "exercise_id": exercise["id"],
            "exercise_order": 1,
            "notes": "Pause all reps",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["workout_day_id"] == setup["day"]["id"]
    assert data["exercise_id"] == exercise["id"]
    assert data["exercise_order"] == 1
    assert data["notes"] == "Pause all reps"


def test_create_workout_exercise_with_missing_day_returns_404(override_current_user):
    exercise = create_test_exercise(name=f"Squat {uuid4().hex}")

    response = client.post(
        "/workout-days/999999/exercises",
        json={
            "exercise_id": exercise["id"],
            "exercise_order": 1,
            "notes": "Invalid workout day",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout day not found"


def test_create_workout_exercise_with_missing_exercise_returns_404(override_current_user):
    setup = create_test_workout_day_setup()

    response = client.post(
        f"/workout-days/{setup['day']['id']}/exercises",
        json={
            "exercise_id": 999999,
            "exercise_order": 1,
            "notes": "Invalid exercise",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise not found"


def test_list_workout_exercises(override_current_user):
    setup = create_test_workout_day_setup()

    exercise_1 = create_test_exercise(name=f"Bench Press {uuid4().hex}")
    exercise_2 = create_test_exercise(name=f"Pull Up {uuid4().hex}")

    workout_exercise_1 = create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=exercise_1["id"],
        exercise_order=1,
    )

    workout_exercise_2 = create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=exercise_2["id"],
        exercise_order=2,
    )

    response = client.get(f"/workout-days/{setup['day']['id']}/exercises")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    workout_exercise_ids = [item["id"] for item in data]

    assert workout_exercise_1["id"] in workout_exercise_ids
    assert workout_exercise_2["id"] in workout_exercise_ids


def test_list_workout_exercises_only_returns_exercises_for_that_day(override_current_user):
    setup = create_test_workout_day_setup()

    day_2 = create_test_workout_day(
        week_id=setup["week"]["id"],
        name="Lower Day",
        day_order=2,
    )

    exercise_1 = create_test_exercise(name=f"Bench Press {uuid4().hex}")
    exercise_2 = create_test_exercise(name=f"Squat {uuid4().hex}")

    day_1_workout_exercise = create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=exercise_1["id"],
        exercise_order=1,
    )

    day_2_workout_exercise = create_test_workout_exercise(
        day_id=day_2["id"],
        exercise_id=exercise_2["id"],
        exercise_order=1,
    )

    response = client.get(f"/workout-days/{setup['day']['id']}/exercises")

    assert response.status_code == 200

    data = response.json()
    workout_exercise_ids = [item["id"] for item in data]

    assert day_1_workout_exercise["id"] in workout_exercise_ids
    assert day_2_workout_exercise["id"] not in workout_exercise_ids


def test_list_workout_exercises_orders_by_exercise_order(override_current_user):
    setup = create_test_workout_day_setup()

    exercise_1 = create_test_exercise(name=f"Exercise A {uuid4().hex}")
    exercise_2 = create_test_exercise(name=f"Exercise B {uuid4().hex}")
    exercise_3 = create_test_exercise(name=f"Exercise C {uuid4().hex}")

    create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=exercise_1["id"],
        exercise_order=3,
    )

    create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=exercise_2["id"],
        exercise_order=1,
    )

    create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=exercise_3["id"],
        exercise_order=2,
    )

    response = client.get(f"/workout-days/{setup['day']['id']}/exercises")

    assert response.status_code == 200

    data = response.json()
    exercise_orders = [item["exercise_order"] for item in data]

    assert exercise_orders == sorted(exercise_orders)


def test_list_workout_exercises_with_missing_day_returns_404(override_current_user):
    response = client.get("/workout-days/999999/exercises")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout day not found"


def test_get_workout_exercise(override_current_user):
    setup = create_test_workout_day_setup()
    exercise = create_test_exercise(name=f"Deadlift {uuid4().hex}")

    workout_exercise = create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=exercise["id"],
        exercise_order=1,
        notes="Heavy top set",
    )

    response = client.get(f"/workout-exercises/{workout_exercise['id']}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == workout_exercise["id"]
    assert data["workout_day_id"] == setup["day"]["id"]
    assert data["exercise_id"] == exercise["id"]
    assert data["exercise_order"] == 1
    assert data["notes"] == "Heavy top set"


def test_get_workout_exercise_not_found(override_current_user):
    response = client.get("/workout-exercises/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout exercise not found"


def test_update_workout_exercise(override_current_user):
    setup = create_test_workout_day_setup()

    old_exercise = create_test_exercise(name=f"Old Exercise {uuid4().hex}")
    new_exercise = create_test_exercise(name=f"New Exercise {uuid4().hex}")

    workout_exercise = create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=old_exercise["id"],
        exercise_order=1,
        notes="Old notes",
    )

    response = client.patch(
        f"/workout-exercises/{workout_exercise['id']}",
        json={
            "exercise_id": new_exercise["id"],
            "exercise_order": 2,
            "notes": "Updated notes",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == workout_exercise["id"]
    assert data["workout_day_id"] == setup["day"]["id"]
    assert data["exercise_id"] == new_exercise["id"]
    assert data["exercise_order"] == 2
    assert data["notes"] == "Updated notes"


def test_update_workout_exercise_partial_keeps_existing_fields(override_current_user):
    setup = create_test_workout_day_setup()
    exercise = create_test_exercise(name=f"Bench Press {uuid4().hex}")

    workout_exercise = create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=exercise["id"],
        exercise_order=1,
        notes="Original notes",
    )

    response = client.patch(
        f"/workout-exercises/{workout_exercise['id']}",
        json={
            "notes": "Only notes changed",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == workout_exercise["id"]
    assert data["workout_day_id"] == setup["day"]["id"]
    assert data["exercise_id"] == exercise["id"]
    assert data["exercise_order"] == 1
    assert data["notes"] == "Only notes changed"


def test_update_workout_exercise_with_missing_exercise_returns_404(override_current_user):
    setup = create_test_workout_day_setup()
    exercise = create_test_exercise(name=f"Bench Press {uuid4().hex}")

    workout_exercise = create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=exercise["id"],
        exercise_order=1,
    )

    response = client.patch(
        f"/workout-exercises/{workout_exercise['id']}",
        json={
            "exercise_id": 999999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Exercise not found"


def test_update_workout_exercise_not_found(override_current_user):
    response = client.patch(
        "/workout-exercises/999999",
        json={
            "notes": "Does not exist",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout exercise not found"


def test_delete_workout_exercise(override_current_user):
    setup = create_test_workout_day_setup()
    exercise = create_test_exercise(name=f"Dip {uuid4().hex}")

    workout_exercise = create_test_workout_exercise(
        day_id=setup["day"]["id"],
        exercise_id=exercise["id"],
        exercise_order=1,
    )

    delete_response = client.delete(f"/workout-exercises/{workout_exercise['id']}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/workout-exercises/{workout_exercise['id']}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Workout exercise not found"


def test_delete_workout_exercise_not_found(override_current_user):
    response = client.delete("/workout-exercises/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout exercise not found"


def test_create_workout_exercise_without_auth_returns_401():
    response = client.post(
        "/workout-days/999999/exercises",
        json={
            "exercise_id": 999999,
            "exercise_order": 1,
            "notes": "This should fail without auth",
        },
    )

    assert response.status_code == 401