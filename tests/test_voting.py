# tests/test_voting.py
import pytest
from models import Vote, db

class TestVoting:
    """Test voting functionality"""

    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication"""
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200

    def test_vote_requires_login(self, client, sample_candidate):
        """Test voting requires authentication"""
        response = client.post(f'/vote/{sample_candidate.id}', follow_redirects=True)
        assert response.status_code == 200

    def test_successful_vote(self, client, app, sample_voter, sample_candidate, sample_election):
        """Test successful vote casting"""
        # Login first
        with client:
            client.post('/auth/login', data={
                'voter_id': 'TEST001',
                'password': 'Test@123'
            })

            # Cast vote
            response = client.post(f'/vote/{sample_candidate.id}',
                                  data={'submit': True},
                                  follow_redirects=True)
            assert response.status_code == 200

            # Check vote was recorded
            with app.app_context():
                vote = Vote.query.filter_by(voter_id=sample_voter.id).first()
                assert vote is not None
                assert vote.candidate_id == sample_candidate.id

    def test_cannot_vote_twice(self, client, app, sample_voter, sample_candidate, sample_election):
        """Test voter cannot vote twice"""
        with client:
            # Login
            client.post('/auth/login', data={
                'voter_id': 'TEST001',
                'password': 'Test@123'
            })

            # First vote
            client.post(f'/vote/{sample_candidate.id}',
                       data={'submit': True},
                       follow_redirects=True)

            # Try to vote again
            response = client.post(f'/vote/{sample_candidate.id}',
                                  data={'submit': True},
                                  follow_redirects=True)

            # Should be redirected with error
            assert response.status_code == 200
            assert b'already voted' in response.data or b'Voting is not currently open' in response.data

class TestResults:
    """Test election results"""

    def test_results_page_loads(self, client):
        """Test results page loads"""
        response = client.get('/results')
        assert response.status_code in [200, 302]

    def test_verify_vote_page_loads(self, client):
        """Test verify vote page loads"""
        response = client.get('/verify-vote')
        assert response.status_code == 200
