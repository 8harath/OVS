# tests/conftest.py
import pytest
from app import create_app
from models import db, Voter, Candidate, Election
from datetime import datetime, timedelta

@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def sample_voter(app):
    """Create a sample voter for testing"""
    with app.app_context():
        voter = Voter(
            name='Test',
            last_name='User',
            email='test@example.com',
            date_of_birth=datetime(1990, 1, 1).date(),
            phone_number='+1234567890',
            address='123 Test St',
            voter_id='TEST001',
            is_verified=True
        )
        voter.set_password('Test@123')
        db.session.add(voter)
        db.session.commit()
        return voter

@pytest.fixture
def sample_admin(app):
    """Create a sample admin for testing"""
    with app.app_context():
        admin = Voter(
            name='Admin',
            last_name='User',
            email='admin@example.com',
            date_of_birth=datetime(1990, 1, 1).date(),
            phone_number='+1234567890',
            address='123 Admin St',
            voter_id='ADMIN001',
            is_admin=True,
            is_verified=True
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def sample_candidate(app):
    """Create a sample candidate for testing"""
    with app.app_context():
        candidate = Candidate(
            name='John Doe',
            party='Test Party',
            photo_url='/static/test.jpg',
            promises='Test promises',
            assets='Test assets',
            liabilities='Test liabilities',
            background='Test background',
            political_views='Test views',
            regional_views='Test regional views'
        )
        db.session.add(candidate)
        db.session.commit()
        return candidate

@pytest.fixture
def sample_election(app):
    """Create a sample election for testing"""
    with app.app_context():
        election = Election(
            title='Test Election',
            description='Test Description',
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        db.session.add(election)
        db.session.commit()
        return election
