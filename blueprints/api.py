# blueprints/api.py
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Voter, Candidate, Vote, Election
from decorators import admin_required
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Helper function for API responses
def api_response(data=None, message=None, status=200, error=None):
    """Standardized API response format"""
    response = {}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    if error:
        response['error'] = error
    return jsonify(response), status

# Candidates API
@api_bp.route('/candidates', methods=['GET'])
def get_candidates():
    """Get all active candidates"""
    try:
        candidates = Candidate.query.filter_by(is_active=True).all()
        data = [{
            'id': c.id,
            'name': c.name,
            'party': c.party,
            'photo_url': c.photo_url,
            'promises': c.promises,
            'vote_count': c.vote_count
        } for c in candidates]

        return api_response(data=data, message='Candidates retrieved successfully')
    except Exception as e:
        return api_response(error=str(e), status=500)

@api_bp.route('/candidates/<int:candidate_id>', methods=['GET'])
def get_candidate(candidate_id):
    """Get candidate details"""
    try:
        candidate = Candidate.query.get_or_404(candidate_id)
        data = {
            'id': candidate.id,
            'name': candidate.name,
            'party': candidate.party,
            'photo_url': candidate.photo_url,
            'promises': candidate.promises,
            'assets': candidate.assets,
            'liabilities': candidate.liabilities,
            'background': candidate.background,
            'political_views': candidate.political_views,
            'regional_views': candidate.regional_views,
            'education': candidate.education,
            'experience': candidate.experience,
            'vote_count': candidate.vote_count
        }

        return api_response(data=data, message='Candidate details retrieved successfully')
    except Exception as e:
        return api_response(error=str(e), status=404)

# Elections API
@api_bp.route('/elections', methods=['GET'])
def get_elections():
    """Get all active elections"""
    try:
        elections = Election.query.filter_by(is_active=True).all()
        data = [{
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'start_date': e.start_date.isoformat(),
            'end_date': e.end_date.isoformat(),
            'is_ongoing': e.is_ongoing(),
            'has_ended': e.has_ended()
        } for e in elections]

        return api_response(data=data, message='Elections retrieved successfully')
    except Exception as e:
        return api_response(error=str(e), status=500)

@api_bp.route('/elections/<int:election_id>', methods=['GET'])
def get_election(election_id):
    """Get election details"""
    try:
        election = Election.query.get_or_404(election_id)
        data = {
            'id': election.id,
            'title': election.title,
            'description': election.description,
            'start_date': election.start_date.isoformat(),
            'end_date': election.end_date.isoformat(),
            'is_active': election.is_active,
            'is_ongoing': election.is_ongoing(),
            'has_ended': election.has_ended(),
            'enable_live_results': election.enable_live_results
        }

        return api_response(data=data, message='Election details retrieved successfully')
    except Exception as e:
        return api_response(error=str(e), status=404)

# Results API
@api_bp.route('/results', methods=['GET'])
def get_results():
    """Get election results"""
    try:
        election = Election.query.filter_by(is_active=True).first()

        # Check if results should be available
        if not election:
            return api_response(error='No active election found', status=404)

        can_view = election.enable_live_results or election.has_ended()
        if not can_view and not (current_user.is_authenticated and current_user.is_admin):
            return api_response(error='Results not yet available', status=403)

        candidates = Candidate.query.filter_by(is_active=True).all()
        total_votes = Vote.query.count()

        results = []
        for candidate in candidates:
            vote_count = candidate.vote_count
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            results.append({
                'candidate_id': candidate.id,
                'name': candidate.name,
                'party': candidate.party,
                'votes': vote_count,
                'percentage': round(percentage, 2)
            })

        # Sort by votes descending
        results.sort(key=lambda x: x['votes'], reverse=True)

        data = {
            'total_votes': total_votes,
            'results': results
        }

        return api_response(data=data, message='Results retrieved successfully')
    except Exception as e:
        return api_response(error=str(e), status=500)

# Statistics API
@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get voting statistics"""
    try:
        total_voters = Voter.query.filter_by(is_verified=True).count()
        voted_count = Voter.query.filter_by(has_voted=True).count()
        turnout_percentage = (voted_count / total_voters * 100) if total_voters > 0 else 0

        data = {
            'total_voters': total_voters,
            'voted_count': voted_count,
            'pending_votes': total_voters - voted_count,
            'turnout_percentage': round(turnout_percentage, 2)
        }

        return api_response(data=data, message='Statistics retrieved successfully')
    except Exception as e:
        return api_response(error=str(e), status=500)

# Vote Verification API
@api_bp.route('/verify-vote/<reference_number>', methods=['GET'])
def verify_vote_api(reference_number):
    """Verify a vote by reference number"""
    try:
        vote = Vote.query.filter_by(reference_number=reference_number).first()

        if not vote:
            return api_response(error='Invalid reference number', status=404)

        data = {
            'reference_number': vote.reference_number,
            'timestamp': vote.timestamp.isoformat(),
            'candidate_name': vote.candidate.name,
            'status': 'confirmed'
        }

        return api_response(data=data, message='Vote verified successfully')
    except Exception as e:
        return api_response(error=str(e), status=500)

# User Profile API (requires authentication)
@api_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile"""
    try:
        data = {
            'id': current_user.id,
            'voter_id': current_user.voter_id,
            'name': f'{current_user.name} {current_user.last_name}',
            'email': current_user.email,
            'has_voted': current_user.has_voted,
            'is_verified': current_user.is_verified,
            'mfa_enabled': current_user.mfa_enabled
        }

        return api_response(data=data, message='Profile retrieved successfully')
    except Exception as e:
        return api_response(error=str(e), status=500)

# Admin APIs
@api_bp.route('/admin/stats', methods=['GET'])
@login_required
@admin_required
def get_admin_stats():
    """Get admin statistics"""
    try:
        total_voters = Voter.query.count()
        verified_voters = Voter.query.filter_by(is_verified=True).count()
        voted_count = Voter.query.filter_by(has_voted=True).count()
        total_candidates = Candidate.query.filter_by(is_active=True).count()
        total_votes = Vote.query.count()

        data = {
            'total_voters': total_voters,
            'verified_voters': verified_voters,
            'pending_verification': total_voters - verified_voters,
            'voted_count': voted_count,
            'total_candidates': total_candidates,
            'total_votes': total_votes,
            'turnout': round((voted_count / verified_voters * 100) if verified_voters > 0 else 0, 2)
        }

        return api_response(data=data, message='Admin statistics retrieved successfully')
    except Exception as e:
        return api_response(error=str(e), status=500)

# Health check
@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check"""
    return api_response(data={'status': 'healthy'}, message='API is running')
