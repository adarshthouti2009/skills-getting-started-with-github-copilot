"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the /activities endpoint"""

    def test_get_activities_returns_all_activities(self):
        """Test that we can fetch all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert len(data) > 0

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupEndpoint:
    """Test the /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity(self):
        """Test signing up for an activity"""
        response = client.post(
            "/activities/Basketball Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_appears_in_participants(self):
        """Test that signed up participant appears in activity"""
        test_email = "participant@mergington.edu"
        
        # Sign up
        response = client.post(
            f"/activities/Tennis Club/signup?email={test_email}"
        )
        assert response.status_code == 200
        
        # Fetch activities and verify participant is there
        response = client.get("/activities")
        activities = response.json()
        assert test_email in activities["Tennis Club"]["participants"]

    def test_signup_duplicate_email_fails(self):
        """Test that signing up twice with the same email fails"""
        test_email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response = client.post(
            f"/activities/Art Studio/signup?email={test_email}"
        )
        assert response.status_code == 200
        
        # Second signup should fail
        response = client.post(
            f"/activities/Art Studio/signup?email={test_email}"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self):
        """Test that signing up for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Test the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_from_activity(self):
        """Test unregistering from an activity"""
        test_email = "unregister_test@mergington.edu"
        
        # First, sign up
        client.post(
            f"/activities/Music Band/signup?email={test_email}"
        )
        
        # Then unregister
        response = client.post(
            f"/activities/Music Band/unregister?email={test_email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]

    def test_unregister_removes_from_participants(self):
        """Test that unregistered participant is removed from activity"""
        test_email = "remove_me@mergington.edu"
        
        # Sign up
        client.post(
            f"/activities/Debate Team/signup?email={test_email}"
        )
        
        # Verify they're registered
        response = client.get("/activities")
        assert test_email in response.json()["Debate Team"]["participants"]
        
        # Unregister
        client.post(
            f"/activities/Debate Team/unregister?email={test_email}"
        )
        
        # Verify they're no longer registered
        response = client.get("/activities")
        assert test_email not in response.json()["Debate Team"]["participants"]

    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregistering from non-existent activity fails"""
        response = client.post(
            "/activities/Fake Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_not_registered_fails(self):
        """Test that unregistering when not registered fails"""
        response = client.post(
            "/activities/Robotics Club/unregister?email=not_registered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_redirects_to_index(self):
        """Test that root path redirects to index.html"""
        response = client.get("/", follow_redirects=True)
        # The response should be successful (200) after redirect
        assert response.status_code == 200
