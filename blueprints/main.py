# blueprints/main.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Voter, Candidate, Vote, Election, Announcement, BlockchainVote
from forms import VoteForm, VerifyVoteForm
from utils import generate_reference_number, get_client_ip, get_user_agent, send_vote_confirmation_email, log_activity
from decorators import verified_required, not_voted_required
from datetime import datetime
import uuid
import sys
import os

# Add parent directory to path to import blockchain_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from blockchain_service import BlockchainService
    BLOCKCHAIN_SERVICE_AVAILABLE = True
except ImportError as e:
    BLOCKCHAIN_SERVICE_AVAILABLE = False
    print(f"Warning: BlockchainService not available: {e}")

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page"""
    elections = Election.query.filter_by(is_active=True).all()
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(5).all()
    return render_template('index.html', elections=elections, announcements=announcements)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    candidates = Candidate.query.filter_by(is_active=True).all()
    election = Election.query.filter_by(is_active=True).first()

    # Get voter stats if admin
    voter_stats = None
    if current_user.is_admin:
        total_voters = Voter.query.count()
        voted_count = Voter.query.filter_by(has_voted=True).count()
        verified_count = Voter.query.filter_by(is_verified=True).count()
        voter_stats = {
            'total': total_voters,
            'voted': voted_count,
            'verified': verified_count,
            'pending': total_voters - verified_count
        }

    return render_template('dashboard.html',
                         user=current_user,
                         candidates=candidates,
                         election=election,
                         voter_stats=voter_stats)

@main_bp.route('/candidate/<int:candidate_id>')
@login_required
def candidate_detail(candidate_id):
    """View candidate details"""
    candidate = Candidate.query.get_or_404(candidate_id)
    return render_template('candidate_detail.html', candidate=candidate)

@main_bp.route('/candidates/compare')
@login_required
def compare_candidates():
    """Compare multiple candidates side by side"""
    candidate_ids = request.args.getlist('ids', type=int)
    candidates = []
    if candidate_ids:
        candidates = Candidate.query.filter(Candidate.id.in_(candidate_ids)).all()
    else:
        candidates = Candidate.query.filter_by(is_active=True).limit(3).all()

    return render_template('compare_candidates.html', candidates=candidates)

@main_bp.route('/vote/<int:candidate_id>', methods=['GET', 'POST'])
@login_required
@verified_required
@not_voted_required
def vote(candidate_id):
    """Cast a vote"""
    candidate = Candidate.query.get_or_404(candidate_id)
    election = Election.query.filter_by(is_active=True).first()

    if not election or not election.is_ongoing():
        flash('Voting is not currently open.', 'error')
        return redirect(url_for('main.dashboard'))

    form = VoteForm()
    if form.validate_on_submit():
        blockchain_error = None
        try:
            # Create vote record
            reference_number = generate_reference_number()
            vote = Vote(
                voter_id=current_user.id,
                candidate_id=candidate_id,
                timestamp=datetime.utcnow(),
                reference_number=reference_number,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )

            # Update voter status
            current_user.has_voted = True

            db.session.add(vote)
            db.session.commit()

            # ========== BLOCKCHAIN INTEGRATION (Phase 1) ==========
            # Record vote on blockchain if enabled
            if current_app.config.get('BLOCKCHAIN_ENABLED', False) and BLOCKCHAIN_SERVICE_AVAILABLE:
                try:
                    # Initialize blockchain service
                    blockchain_config = {
                        'BLOCKCHAIN_NETWORK': current_app.config.get('BLOCKCHAIN_NETWORK', 'mumbai'),
                        'MUMBAI_RPC_URL': current_app.config.get('MUMBAI_RPC_URL', ''),
                        'POLYGON_RPC_URL': current_app.config.get('POLYGON_RPC_URL', ''),
                        'BLOCKCHAIN_PRIVATE_KEY': current_app.config.get('BLOCKCHAIN_PRIVATE_KEY', ''),
                        'VOTE_REGISTRY_ADDRESS': current_app.config.get('VOTE_REGISTRY_ADDRESS', ''),
                        'ELECTION_MANAGER_ADDRESS': current_app.config.get('ELECTION_MANAGER_ADDRESS', ''),
                        'VOTER_REGISTRY_ADDRESS': current_app.config.get('VOTER_REGISTRY_ADDRESS', '')
                    }

                    blockchain_service = BlockchainService(blockchain_config)

                    # Record vote on blockchain
                    blockchain_result = blockchain_service.record_vote(
                        voter_id=current_user.voter_id,
                        candidate_id=candidate_id,
                        election_id=election.id,
                        reference_number=reference_number
                    )

                    if blockchain_result['success']:
                        # Save blockchain record to database
                        blockchain_vote = BlockchainVote(
                            vote_id=vote.id,
                            vote_hash=blockchain_result['vote_hash'],
                            transaction_hash=blockchain_result['tx_hash'],
                            block_number=blockchain_result['block_number'],
                            blockchain_timestamp=blockchain_result['timestamp'],
                            gas_used=blockchain_result.get('gas_used'),
                            status='confirmed'
                        )
                        db.session.add(blockchain_vote)
                        db.session.commit()

                        log_activity(current_user.id, 'BLOCKCHAIN_VOTE_RECORDED',
                                   f'Vote recorded on blockchain: {blockchain_result["tx_hash"]}')
                    else:
                        blockchain_error = blockchain_result.get('error', 'Unknown blockchain error')

                except Exception as bc_error:
                    blockchain_error = str(bc_error)
                    log_activity(current_user.id, 'BLOCKCHAIN_ERROR',
                               f'Failed to record vote on blockchain: {blockchain_error}')

                    # If configured to fail gracefully, continue without blockchain
                    if not current_app.config.get('BLOCKCHAIN_FAIL_GRACEFULLY', True):
                        # Rollback the vote if blockchain is required
                        db.session.rollback()
                        flash(f'Blockchain recording failed: {blockchain_error}', 'error')
                        return redirect(url_for('main.dashboard'))
            # ======================================================

            # Send confirmation email
            send_vote_confirmation_email(current_user, vote)
            log_activity(current_user.id, 'VOTED', f'Voted for candidate: {candidate.name}')

            # Flash success message with blockchain info
            success_message = f'Thank you for voting! Your reference number is {reference_number}'
            if blockchain_error:
                success_message += ' (Note: Blockchain recording failed, but your vote was counted)'
            flash(success_message, 'success')

            return redirect(url_for('main.vote_confirmation', reference_number=reference_number))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while casting your vote: {str(e)}', 'error')
            return redirect(url_for('main.dashboard'))

    return render_template('vote.html', candidate=candidate, form=form)

@main_bp.route('/vote-confirmation/<reference_number>')
@login_required
def vote_confirmation(reference_number):
    """Show vote confirmation"""
    vote = Vote.query.filter_by(reference_number=reference_number, voter_id=current_user.id).first_or_404()
    return render_template('vote_confirmation.html', vote=vote, candidate=vote.candidate)

@main_bp.route('/verify-vote', methods=['GET', 'POST'])
def verify_vote():
    """Verify a vote using reference number"""
    form = VerifyVoteForm()
    vote_info = None
    blockchain_info = None

    if form.validate_on_submit():
        vote = Vote.query.filter_by(reference_number=form.reference_number.data).first()
        if vote:
            vote_info = {
                'timestamp': vote.timestamp,
                'candidate_name': vote.candidate.name,
                'status': 'confirmed'
            }

            # Check if vote has blockchain record
            blockchain_record = BlockchainVote.query.filter_by(vote_id=vote.id).first()
            if blockchain_record:
                blockchain_info = {
                    'transaction_hash': blockchain_record.transaction_hash,
                    'block_number': blockchain_record.block_number,
                    'blockchain_timestamp': blockchain_record.blockchain_timestamp,
                    'vote_hash': blockchain_record.vote_hash,
                    'status': blockchain_record.status,
                    'explorer_url': _get_blockchain_explorer_url(
                        blockchain_record.transaction_hash,
                        current_app.config.get('BLOCKCHAIN_NETWORK', 'mumbai')
                    )
                }

                # Optionally verify on-chain
                if current_app.config.get('BLOCKCHAIN_ENABLED', False) and BLOCKCHAIN_SERVICE_AVAILABLE:
                    try:
                        blockchain_config = {
                            'BLOCKCHAIN_NETWORK': current_app.config.get('BLOCKCHAIN_NETWORK', 'mumbai'),
                            'MUMBAI_RPC_URL': current_app.config.get('MUMBAI_RPC_URL', ''),
                            'POLYGON_RPC_URL': current_app.config.get('POLYGON_RPC_URL', ''),
                            'BLOCKCHAIN_PRIVATE_KEY': current_app.config.get('BLOCKCHAIN_PRIVATE_KEY', ''),
                            'VOTE_REGISTRY_ADDRESS': current_app.config.get('VOTE_REGISTRY_ADDRESS', ''),
                            'ELECTION_MANAGER_ADDRESS': current_app.config.get('ELECTION_MANAGER_ADDRESS', ''),
                            'VOTER_REGISTRY_ADDRESS': current_app.config.get('VOTER_REGISTRY_ADDRESS', '')
                        }
                        blockchain_service = BlockchainService(blockchain_config)
                        verification = blockchain_service.verify_vote(form.reference_number.data)

                        if verification['exists']:
                            blockchain_info['on_chain_verified'] = True
                            blockchain_info['on_chain_vote_hash'] = verification['vote_hash']
                    except Exception as e:
                        blockchain_info['verification_error'] = str(e)

            flash('Your vote has been verified!', 'success')
        else:
            flash('Invalid reference number. Please check and try again.', 'error')

    return render_template('verify_vote.html', form=form, vote_info=vote_info, blockchain_info=blockchain_info)


def _get_blockchain_explorer_url(tx_hash, network):
    """Get blockchain explorer URL for transaction"""
    if network == 'mumbai':
        return f'https://mumbai.polygonscan.com/tx/{tx_hash}'
    elif network == 'polygon':
        return f'https://polygonscan.com/tx/{tx_hash}'
    else:
        return None

@main_bp.route('/results')
def results():
    """View election results"""
    election = Election.query.filter_by(is_active=True).first()

    # Check if results should be displayed
    can_view_results = False
    if election:
        if election.enable_live_results or election.has_ended():
            can_view_results = True
        elif current_user.is_authenticated and current_user.is_admin:
            can_view_results = True

    if not can_view_results:
        flash('Election results are not yet available.', 'info')
        return redirect(url_for('main.index'))

    # Get vote counts
    candidates = Candidate.query.filter_by(is_active=True).all()
    total_votes = Vote.query.count()

    results_data = []
    for candidate in candidates:
        vote_count = candidate.vote_count
        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
        results_data.append({
            'candidate': candidate,
            'votes': vote_count,
            'percentage': round(percentage, 2)
        })

    # Sort by votes (descending)
    results_data.sort(key=lambda x: x['votes'], reverse=True)

    return render_template('results.html',
                         results=results_data,
                         total_votes=total_votes,
                         election=election)

@main_bp.route('/statistics')
def statistics():
    """View voting statistics"""
    total_voters = Voter.query.filter_by(is_verified=True).count()
    voted_count = Voter.query.filter_by(has_voted=True).count()
    turnout_percentage = (voted_count / total_voters * 100) if total_voters > 0 else 0

    candidates = Candidate.query.filter_by(is_active=True).all()
    candidate_stats = []
    for candidate in candidates:
        candidate_stats.append({
            'name': candidate.name,
            'party': candidate.party,
            'votes': candidate.vote_count
        })

    stats = {
        'total_voters': total_voters,
        'voted_count': voted_count,
        'turnout_percentage': round(turnout_percentage, 2),
        'candidate_stats': candidate_stats
    }

    return render_template('statistics.html', stats=stats)

@main_bp.route('/announcements')
def announcements():
    """View all announcements"""
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).all()
    return render_template('announcements.html', announcements=announcements)

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@main_bp.route('/faq')
def faq():
    """FAQ page"""
    return render_template('faq.html')

# Error handlers
@main_bp.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@main_bp.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('errors/500.html'), 500
