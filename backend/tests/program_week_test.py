from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_test_program():
    response = client.post(
        "/programs/",
        json={
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


def test_create_program_week(override_current_user):
    program = create_test_program()

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


def test_create_program_week_with_missing_program_returns_404(override_current_user):
    response = client.post(
        "/programs/999999/weeks",
        json={
            "week_number": 1,
            "notes": "Invalid parent program",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"


def test_list_program_weeks(override_current_user):
    program = create_test_program()

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


def test_list_program_weeks_only_returns_weeks_for_that_program(override_current_user):
    program_1 = create_test_program()
    program_2 = create_test_program()

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


def test_list_program_weeks_orders_by_week_number(override_current_user):
    program = create_test_program()

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


def test_list_program_weeks_with_missing_program_returns_404(override_current_user):
    response = client.get("/programs/999999/weeks")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"


def test_get_program_week(override_current_user):
    program = create_test_program()

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


def test_get_program_week_not_found(override_current_user):
    response = client.get("/program-weeks/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program week not found"


def test_update_program_week(override_current_user):
    program = create_test_program()

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


def test_update_program_week_partial_keeps_existing_fields(override_current_user):
    program = create_test_program()

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


def test_update_program_week_not_found(override_current_user):
    response = client.patch(
        "/program-weeks/999999",
        json={
            "notes": "Does not exist",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Program week not found"


def test_delete_program_week(override_current_user):
    program = create_test_program()

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


def test_delete_program_week_not_found(override_current_user):
    response = client.delete("/program-weeks/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Program week not found"


def test_create_program_week_without_auth_returns_401():
    response = client.post(
        "/programs/999999/weeks",
        json={
            "week_number": 1,
            "notes": "This should fail without auth",
        },
    )

    assert response.status_code == 401


def test_create_duplicate_program_week_number_returns_409(override_current_user):
    program = create_test_program()

    create_test_program_week(
        program_id=program["id"],
        week_number=1,
        notes="Original week 1",
    )

    response = client.post(
        f"/programs/{program['id']}/weeks",
        json={
            "week_number": 1,
            "notes": "Duplicate week 1",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Program week with this week number already exists for this program."


def test_same_week_number_allowed_for_different_programs(override_current_user):
    program_1 = create_test_program()
    program_2 = create_test_program()

    week_1 = create_test_program_week(
        program_id=program_1["id"],
        week_number=1,
        notes="Program 1 week 1",
    )

    week_2 = create_test_program_week(
        program_id=program_2["id"],
        week_number=1,
        notes="Program 2 week 1",
    )

    assert week_1["week_number"] == 1
    assert week_2["week_number"] == 1
    assert week_1["program_id"] != week_2["program_id"]