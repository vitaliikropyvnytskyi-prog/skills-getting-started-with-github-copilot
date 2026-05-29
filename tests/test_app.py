import copy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

# Preserve the original activity state so tests can reset it.
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_adds_participant():
    activity_name = "Gym Class"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Unknown%20Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_full_activity_returns_400():
    activity_name = "Chess Club"
    activities[activity_name]["max_participants"] = len(activities[activity_name]["participants"])

    response = client.post(f"/activities/{activity_name}/signup?email=extra@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is already full"


def test_delete_participant_removes_user():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_delete_missing_participant_returns_404():
    activity_name = "Drama Club"
    email = "notregistered@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not registered for this activity"
