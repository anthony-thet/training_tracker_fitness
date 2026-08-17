from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_test_program():
    response = client.post(
        "/programs/",
        json={
            "name": f"Program Detail Test {uuid4().hex}",
            "description": "Program used for detail endpoint tests",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_program_week(program_id: int, week_number: int = 1):
    response = client.post(
        f"/programs/{program_id}/weeks",
        json={
            "week_number": week_number,
            "notes": "Test week notes",
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
            "notes": "Test workout day notes",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_exercise(name: str | None = None):
    exercise_name = name or f"Bench Press {uuid4().hex}"

    response = client.post(
        "/exercises/",
        json={
            "name": exercise_name,
            "category": "Strength",
            "primary_muscle": "Chest",
            "equipment": "Barbell",
            "description": "Test exercise description",
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
            "notes": "Pause all reps",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_planned_set(
    workout_exercise_id: int,
    set_order: int = 1,
    target_reps: int = 5,
    target_weight: float = 225.0,
    target_rpe: float = 7.0,
):
    response = client.post(
        f"/workout-exercises/{workout_exercise_id}/sets",
        json={
            "set_order": set_order,
            "target_reps": target_reps,
            "target_weight": target_weight,
            "target_rpe": target_rpe,
            "notes": "Test planned set notes",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_get_program_detail_returns_nested_program(override_current_user):
    user = override_current_user
    program = create_test_program()

    program_week = create_test_program_week(
        program_id=program["id"],
        week_number=1,
    )

    workout_day = create_test_workout_day(
        week_id=program_week["id"],
        name="Upper 1",
        day_order=1,
    )

    exercise = create_test_exercise(
        name=f"Bench Press {uuid4().hex}",
    )

    workout_exercise = create_test_workout_exercise(
        day_id=workout_day["id"],
        exercise_id=exercise["id"],
        exercise_order=1,
    )

    planned_set_1 = create_test_planned_set(
        workout_exercise_id=workout_exercise["id"],
        set_order=1,
        target_reps=5,
        target_weight=225.0,
        target_rpe=7.0,
    )

    planned_set_2 = create_test_planned_set(
        workout_exercise_id=workout_exercise["id"],
        set_order=2,
        target_reps=5,
        target_weight=225.0,
        target_rpe=8.0,
    )

    response = client.get(f"/programs/{program['id']}/detail")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == program["id"]
    assert data["user_id"] == user.id
    assert data["name"] == program["name"]
    assert data["description"] == program["description"]

    assert "program_weeks" in data
    assert isinstance(data["program_weeks"], list)
    assert len(data["program_weeks"]) == 1

    week_data = data["program_weeks"][0]

    assert week_data["id"] == program_week["id"]
    assert week_data["program_id"] == program["id"]
    assert week_data["week_number"] == 1
    assert week_data["notes"] == "Test week notes"

    assert "workout_days" in week_data
    assert isinstance(week_data["workout_days"], list)
    assert len(week_data["workout_days"]) == 1

    day_data = week_data["workout_days"][0]

    assert day_data["id"] == workout_day["id"]
    assert day_data["program_week_id"] == program_week["id"]
    assert day_data["name"] == "Upper 1"
    assert day_data["day_order"] == 1
    assert day_data["notes"] == "Test workout day notes"

    assert "workout_exercises" in day_data
    assert isinstance(day_data["workout_exercises"], list)
    assert len(day_data["workout_exercises"]) == 1

    workout_exercise_data = day_data["workout_exercises"][0]

    assert workout_exercise_data["id"] == workout_exercise["id"]
    assert workout_exercise_data["workout_day_id"] == workout_day["id"]
    assert workout_exercise_data["exercise_id"] == exercise["id"]
    assert workout_exercise_data["exercise_order"] == 1
    assert workout_exercise_data["notes"] == "Pause all reps"

    assert "exercise" in workout_exercise_data

    exercise_data = workout_exercise_data["exercise"]

    assert exercise_data["id"] == exercise["id"]
    assert exercise_data["name"] == exercise["name"]
    assert exercise_data["category"] == "Strength"
    assert exercise_data["primary_muscle"] == "Chest"
    assert exercise_data["equipment"] == "Barbell"

    assert "planned_sets" in workout_exercise_data
    assert isinstance(workout_exercise_data["planned_sets"], list)
    assert len(workout_exercise_data["planned_sets"]) == 2

    planned_set_ids = [
        planned_set["id"]
        for planned_set in workout_exercise_data["planned_sets"]
    ]

    assert planned_set_1["id"] in planned_set_ids
    assert planned_set_2["id"] in planned_set_ids

    set_orders = [
        planned_set["set_order"]
        for planned_set in workout_exercise_data["planned_sets"]
    ]

    assert set_orders == sorted(set_orders)


def test_get_program_detail_with_empty_program_returns_empty_program_weeks(override_current_user):
    user = override_current_user
    program = create_test_program()

    response = client.get(f"/programs/{program['id']}/detail")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == program["id"]
    assert data["user_id"] == user.id
    assert data["name"] == program["name"]
    assert data["description"] == program["description"]

    assert "program_weeks" in data
    assert data["program_weeks"] == []


def test_get_program_detail_not_found(override_current_user):
    response = client.get("/programs/999999/detail")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"


def test_get_program_detail_without_auth_returns_401():
    response = client.get("/programs/999999/detail")

    assert response.status_code == 401