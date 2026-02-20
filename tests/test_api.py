"""Tests for the FastAPI backend."""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestAuthEndpoints:
    def test_auth_status_returns_structure(self):
        response = client.get("/api/v1/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert "authenticated" in data
        assert isinstance(data["authenticated"], bool)


class TestChannelsEndpoints:
    def test_channels_list_returns_array(self):
        response = client.get("/api/v1/channels")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_channels_list_has_expected_fields(self):
        response = client.get("/api/v1/channels")
        data = response.json()
        if len(data) > 0:
            channel = data[0]
            assert "id" in channel
            assert "name" in channel
            assert "type" in channel


class TestVideosEndpoints:
    def test_videos_list_returns_array(self):
        response = client.get("/api/v1/videos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_videos_list_supports_channel_filter(self):
        response = client.get("/api/v1/videos?channel_id=test123")
        assert response.status_code == 200

    def test_video_detail_not_found(self):
        response = client.get("/api/v1/videos/nonexistent_id")
        assert response.status_code == 404
