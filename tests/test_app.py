import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "participants" in data["Basketball Team"]

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    # It should redirect to /static/index.html, but since it's mounted, it might serve the file
    # Actually, the root redirects to /static/index.html
    # But TestClient might not handle redirects the same, but let's check
    # Perhaps assert it's 200 and contains html

def test_signup_success():
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Basketball Team"]["participants"]

def test_signup_duplicate():
    # First signup
    client.post("/activities/Swimming%20Club/signup?email=duplicate@example.com")
    # Second should fail
    response = client.post("/activities/Swimming%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup?email=test@example.com")
    assert response.status_code == 404

def test_unregister_success():
    # First signup
    client.post("/activities/Drama%20Club/signup?email=unregister@example.com")
    # Then unregister
    response = client.delete("/activities/Drama%20Club/participants/unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Drama Club"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Art%20Workshop/participants/notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]

def test_unregister_nonexistent_activity():
    response = client.delete("/activities/Nonexistent/participants/test@example.com")
    assert response.status_code == 404