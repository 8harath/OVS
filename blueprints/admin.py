# blueprints/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import db, Voter, Candidate, Vote, Election, Announcement
from forms import CandidateForm, ElectionForm, AnnouncementForm
from decorators import admin_required
from utils import save_file, log_activity
from datetime import datetime
import csv
import io

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    # Get statistics
    total_voters = Voter.query.count()
    verified_voters = Voter.query.filter_by(is_verified=True).count()
    voted_count = Voter.query.filter_by(has_voted=True).count()
    total_candidates = Candidate.query.filter_by(is_active=True).count()
    total_votes = Vote.query.count()

    # Recent activity
    recent_voters = Voter.query.order_by(Voter.created_at.desc()).limit(10).all()
    recent_votes = Vote.query.order_by(Vote.timestamp.desc()).limit(10).all()

    stats = {
        'total_voters': total_voters,
        'verified_voters': verified_voters,
        'voted_count': voted_count,
        'total_candidates': total_candidates,
        'total_votes': total_votes,
        'pending_verification': total_voters - verified_voters,
        'turnout': round((voted_count / verified_voters * 100) if verified_voters > 0 else 0, 2)
    }

    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_voters=recent_voters,
                         recent_votes=recent_votes)

# Voter Management
@admin_bp.route('/voters')
@login_required
@admin_required
def voters():
    """List all voters"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '')

    query = Voter.query
    if search:
        query = query.filter(
            (Voter.name.contains(search)) |
            (Voter.last_name.contains(search)) |
            (Voter.voter_id.contains(search)) |
            (Voter.email.contains(search))
        )

    voters = query.order_by(Voter.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('admin/voters.html', voters=voters, search=search)

@admin_bp.route('/voter/<int:voter_id>')
@login_required
@admin_required
def voter_detail(voter_id):
    """View voter details"""
    voter = Voter.query.get_or_404(voter_id)
    return render_template('admin/voter_detail.html', voter=voter)

@admin_bp.route('/voter/<int:voter_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_voter(voter_id):
    """Verify a voter"""
    voter = Voter.query.get_or_404(voter_id)
    voter.is_verified = True
    db.session.commit()
    log_activity(current_user.id, 'VOTER_VERIFIED', f'Verified voter: {voter.voter_id}')
    flash(f'Voter {voter.voter_id} has been verified.', 'success')
    return redirect(url_for('admin.voters'))

@admin_bp.route('/voter/<int:voter_id>/unverify', methods=['POST'])
@login_required
@admin_required
def unverify_voter(voter_id):
    """Unverify a voter"""
    voter = Voter.query.get_or_404(voter_id)
    voter.is_verified = False
    db.session.commit()
    log_activity(current_user.id, 'VOTER_UNVERIFIED', f'Unverified voter: {voter.voter_id}')
    flash(f'Voter {voter.voter_id} verification has been removed.', 'info')
    return redirect(url_for('admin.voters'))

@admin_bp.route('/voter/<int:voter_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_voter(voter_id):
    """Delete a voter"""
    voter = Voter.query.get_or_404(voter_id)
    if voter.is_admin:
        flash('Cannot delete admin users.', 'error')
        return redirect(url_for('admin.voters'))

    db.session.delete(voter)
    db.session.commit()
    log_activity(current_user.id, 'VOTER_DELETED', f'Deleted voter: {voter.voter_id}')
    flash('Voter has been deleted.', 'success')
    return redirect(url_for('admin.voters'))

# Candidate Management
@admin_bp.route('/candidates')
@login_required
@admin_required
def candidates():
    """List all candidates"""
    candidates = Candidate.query.order_by(Candidate.created_at.desc()).all()
    return render_template('admin/candidates.html', candidates=candidates)

@admin_bp.route('/candidate/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_candidate():
    """Add a new candidate"""
    form = CandidateForm()

    if form.validate_on_submit():
        try:
            # Handle photo upload
            photo_url = '/static/images/default-candidate.png'
            if form.photo.data:
                photo_path = save_file(form.photo.data, 'candidates')
                if photo_path:
                    photo_url = '/' + photo_path

            candidate = Candidate(
                name=form.name.data,
                party=form.party.data,
                photo_url=photo_url,
                promises=form.promises.data,
                assets=form.assets.data,
                liabilities=form.liabilities.data,
                background=form.background.data,
                political_views=form.political_views.data,
                regional_views=form.regional_views.data,
                education=form.education.data,
                experience=form.experience.data
            )

            db.session.add(candidate)
            db.session.commit()
            log_activity(current_user.id, 'CANDIDATE_ADDED', f'Added candidate: {candidate.name}')
            flash(f'Candidate {candidate.name} has been added successfully!', 'success')
            return redirect(url_for('admin.candidates'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')

    return render_template('admin/add_candidate.html', form=form)

@admin_bp.route('/candidate/<int:candidate_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_candidate(candidate_id):
    """Edit a candidate"""
    candidate = Candidate.query.get_or_404(candidate_id)
    form = CandidateForm(obj=candidate)

    if form.validate_on_submit():
        try:
            # Handle photo upload
            if form.photo.data:
                photo_path = save_file(form.photo.data, 'candidates')
                if photo_path:
                    candidate.photo_url = '/' + photo_path

            candidate.name = form.name.data
            candidate.party = form.party.data
            candidate.promises = form.promises.data
            candidate.assets = form.assets.data
            candidate.liabilities = form.liabilities.data
            candidate.background = form.background.data
            candidate.political_views = form.political_views.data
            candidate.regional_views = form.regional_views.data
            candidate.education = form.education.data
            candidate.experience = form.experience.data

            db.session.commit()
            log_activity(current_user.id, 'CANDIDATE_UPDATED', f'Updated candidate: {candidate.name}')
            flash(f'Candidate {candidate.name} has been updated!', 'success')
            return redirect(url_for('admin.candidates'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')

    return render_template('admin/edit_candidate.html', form=form, candidate=candidate)

@admin_bp.route('/candidate/<int:candidate_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_candidate(candidate_id):
    """Delete a candidate"""
    candidate = Candidate.query.get_or_404(candidate_id)
    db.session.delete(candidate)
    db.session.commit()
    log_activity(current_user.id, 'CANDIDATE_DELETED', f'Deleted candidate: {candidate.name}')
    flash('Candidate has been deleted.', 'success')
    return redirect(url_for('admin.candidates'))

# Election Management
@admin_bp.route('/elections')
@login_required
@admin_required
def elections():
    """List all elections"""
    elections = Election.query.order_by(Election.created_at.desc()).all()
    return render_template('admin/elections.html', elections=elections)

@admin_bp.route('/election/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_election():
    """Add a new election"""
    form = ElectionForm()

    if form.validate_on_submit():
        try:
            election = Election(
                title=form.title.data,
                description=form.description.data,
                start_date=datetime.combine(form.start_date.data, datetime.min.time()),
                end_date=datetime.combine(form.end_date.data, datetime.max.time()),
                is_active=form.is_active.data,
                enable_live_results=form.enable_live_results.data
            )

            db.session.add(election)
            db.session.commit()
            log_activity(current_user.id, 'ELECTION_CREATED', f'Created election: {election.title}')
            flash(f'Election "{election.title}" has been created!', 'success')
            return redirect(url_for('admin.elections'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')

    return render_template('admin/add_election.html', form=form)

# Announcements Management
@admin_bp.route('/announcements')
@login_required
@admin_required
def announcements():
    """List all announcements"""
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements)

@admin_bp.route('/announcement/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_announcement():
    """Add a new announcement"""
    form = AnnouncementForm()

    if form.validate_on_submit():
        try:
            announcement = Announcement(
                title=form.title.data,
                content=form.content.data,
                is_active=form.is_active.data,
                created_by=current_user.id
            )

            db.session.add(announcement)
            db.session.commit()
            log_activity(current_user.id, 'ANNOUNCEMENT_CREATED', f'Created announcement: {announcement.title}')
            flash('Announcement has been posted!', 'success')
            return redirect(url_for('admin.announcements'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')

    return render_template('admin/add_announcement.html', form=form)

# Reports & Export
@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """View reports"""
    return render_template('admin/reports.html')

@admin_bp.route('/export/voters')
@login_required
@admin_required
def export_voters():
    """Export voters to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['ID', 'Voter ID', 'Name', 'Email', 'Phone', 'Verified', 'Has Voted', 'Registration Date'])

    # Write data
    voters = Voter.query.all()
    for voter in voters:
        writer.writerow([
            voter.id,
            voter.voter_id,
            f'{voter.name} {voter.last_name}',
            voter.email,
            voter.phone_number,
            'Yes' if voter.is_verified else 'No',
            'Yes' if voter.has_voted else 'No',
            voter.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    # Create response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'voters_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@admin_bp.route('/export/results')
@login_required
@admin_required
def export_results():
    """Export election results to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Candidate Name', 'Party', 'Total Votes', 'Percentage'])

    # Write data
    candidates = Candidate.query.filter_by(is_active=True).all()
    total_votes = Vote.query.count()

    for candidate in candidates:
        vote_count = candidate.vote_count
        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
        writer.writerow([
            candidate.name,
            candidate.party,
            vote_count,
            f'{percentage:.2f}%'
        ])

    # Create response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )
