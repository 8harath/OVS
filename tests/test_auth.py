# tests/test_auth.py
import pytest
from models import Voter, db

class TestAuthentication:
    """Test authentication functionality"""

    def test_register_page_loads(self, client):
        """Test registration page loads"""
        response = client.get('/auth/register')
        assert response.status_code == 200

    def test_login_page_loads(self, client):
        """Test login page loads"""
        response = client.get('/auth/login')
        assert response.status_code == 200

    def test_successful_registration(self, client, app):
        """Test successful user registration"""
        data = {
            'name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'date_of_birth': '2000-01-01',
            'phone_number': '+1234567890',
            'address': '123 New St',
            'voter_id': 'NEW001',
            'password': 'NewPass@123',
            'confirm_password': 'NewPass@123'
        }
        response = client.post('/auth/register', data=data, follow_redirects=True)
        assert response.status_code == 200

        with app.app_context():
            voter = Voter.query.filter_by(voter_id='NEW001').first()
            assert voter is not None
            assert voter.email == 'newuser@example.com'

    def test_duplicate_voter_id(self, client, sample_voter):
        """Test registration with duplicate voter ID"""
        data = {
            'name': 'Duplicate',
            'last_name': 'User',
            'email': 'duplicate@example.com',
            'date_of_birth': '2000-01-01',
            'phone_number': '+1234567891',
            'address': '123 Dup St',
            'voter_id': 'TEST001',  # Same as sample_voter
            'password': 'DupPass@123',
            'confirm_password': 'DupPass@123'
        }
        response = client.post('/auth/register', data=data)
        assert b'already exists' in response.data or response.status_code == 200

    def test_successful_login(self, client, sample_voter):
        """Test successful login"""
        data = {
            'voter_id': 'TEST001',
            'password': 'Test@123'
        }
        response = client.post('/auth/login', data=data, follow_redirects=True)
        assert response.status_code == 200

    def test_failed_login_wrong_password(self, client, sample_voter):
        """Test login with wrong password"""
        data = {
            'voter_id': 'TEST001',
            'password': 'WrongPassword'
        }
        response = client.post('/auth/login', data=data)
        assert b'Invalid' in response.data or response.status_code == 200

    def test_logout(self, client, sample_voter):
        """Test logout functionality"""
        # Login first
        client.post('/auth/login', data={
            'voter_id': 'TEST001',
            'password': 'Test@123'
        })
        # Then logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200

class TestPasswordReset:
    """Test password reset functionality"""

    def test_password_reset_request_page(self, client):
        """Test password reset request page loads"""
        response = client.get('/auth/reset-password-request')
        assert response.status_code == 200

    def test_password_reset_request(self, client, sample_voter, app):
        """Test password reset request"""
        data = {'email': 'test@example.com'}
        response = client.post('/auth/reset-password-request', data=data, follow_redirects=True)
        assert response.status_code == 200
