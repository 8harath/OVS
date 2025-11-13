# tests/test_api.py
import pytest
import json

class TestAPI:
    """Test API endpoints"""

    def test_api_health_check(self, client):
        """Test API health check endpoint"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['status'] == 'healthy'

    def test_get_candidates(self, client, sample_candidate):
        """Test get candidates API"""
        response = client.get('/api/v1/candidates')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert len(data['data']) > 0

    def test_get_candidate_detail(self, client, sample_candidate):
        """Test get candidate detail API"""
        response = client.get(f'/api/v1/candidates/{sample_candidate.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['name'] == 'John Doe'

    def test_get_elections(self, client, sample_election):
        """Test get elections API"""
        response = client.get('/api/v1/elections')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data

    def test_get_statistics(self, client):
        """Test get statistics API"""
        response = client.get('/api/v1/statistics')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert 'total_voters' in data['data']
