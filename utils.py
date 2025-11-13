# utils.py
import os
import re
import uuid
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from flask import current_app, render_template
import logging

mail = Mail()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voting_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'pdf'})
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, folder='uploads'):
    """Save uploaded file and return the file path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add unique identifier to prevent filename conflicts
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        return file_path
    return None

def send_email(to, subject, template, **kwargs):
    """Send email using Flask-Mail"""
    try:
        msg = Message(
            subject,
            recipients=[to],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        msg.html = render_template(f'emails/{template}.html', **kwargs)
        mail.send(msg)
        logger.info(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        return False

def send_registration_email(voter):
    """Send registration confirmation email"""
    return send_email(
        to=voter.email,
        subject='Registration Successful - Online Voting System',
        template='registration',
        voter=voter
    )

def send_vote_confirmation_email(voter, vote):
    """Send vote confirmation email"""
    return send_email(
        to=voter.email,
        subject='Vote Confirmation - Online Voting System',
        template='vote_confirmation',
        voter=voter,
        vote=vote
    )

def send_password_reset_email(voter, reset_url):
    """Send password reset email"""
    return send_email(
        to=voter.email,
        subject='Password Reset Request - Online Voting System',
        template='password_reset',
        voter=voter,
        reset_url=reset_url
    )

def validate_password(password):
    """Validate password strength"""
    errors = []

    min_length = current_app.config.get('MIN_PASSWORD_LENGTH', 8)
    if len(password) < min_length:
        errors.append(f'Password must be at least {min_length} characters long.')

    if current_app.config.get('REQUIRE_UPPERCASE', True) and not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter.')

    if current_app.config.get('REQUIRE_LOWERCASE', True) and not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter.')

    if current_app.config.get('REQUIRE_DIGITS', True) and not re.search(r'\d', password):
        errors.append('Password must contain at least one digit.')

    if current_app.config.get('REQUIRE_SPECIAL_CHARS', True) and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character.')

    return errors

def generate_reference_number():
    """Generate a unique reference number for votes"""
    return str(uuid.uuid4())

def get_client_ip(request):
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    return request.environ.get('REMOTE_ADDR', 'unknown')

def get_user_agent(request):
    """Get user agent from request"""
    return request.headers.get('User-Agent', 'unknown')

def format_vote_count(count):
    """Format vote count with commas"""
    return f"{count:,}"

def calculate_percentage(part, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return round((part / total) * 100, 2)

def log_activity(user_id, action, details=''):
    """Log user activity"""
    logger.info(f"User {user_id} - {action} - {details}")

def create_sample_data(db):
    """Create sample candidates and admin user for testing"""
    from models import Candidate, Voter, Election
    from datetime import datetime, timedelta

    # Check if admin exists
    admin = Voter.query.filter_by(is_admin=True).first()
    if not admin:
        admin = Voter(
            name='Admin',
            last_name='User',
            email=current_app.config.get('ADMIN_EMAIL', 'admin@votingsystem.com'),
            date_of_birth=datetime(1990, 1, 1).date(),
            phone_number='+1234567890',
            address='Admin Address',
            voter_id='ADMIN001',
            is_admin=True,
            is_verified=True
        )
        admin.set_password(current_app.config.get('ADMIN_PASSWORD', 'Admin@123'))
        db.session.add(admin)
        logger.info("Admin user created")

    # Check if candidates exist
    if Candidate.query.count() == 0:
        candidates = [
            Candidate(
                name='John Doe',
                party='Democratic Party',
                photo_url='/static/images/candidates/john_doe.jpg',
                promises='Improve healthcare\nCreate more jobs\nEnhance education system',
                assets='Property worth $500,000\nBusiness investments',
                liabilities='Bank loan: $100,000',
                background='Former senator with 10 years of experience',
                political_views='Progressive reforms and social welfare',
                regional_views='Focus on urban development',
                education='MBA from Harvard University',
                experience='Senator (2010-2020), City Council Member (2005-2010)'
            ),
            Candidate(
                name='Jane Smith',
                party='Republican Party',
                photo_url='/static/images/candidates/jane_smith.jpg',
                promises='Lower taxes\nStrengthen economy\nImprove infrastructure',
                assets='Real estate worth $800,000\nStock portfolio',
                liabilities='Mortgage: $200,000',
                background='Business executive and community leader',
                political_views='Conservative economic policies',
                regional_views='Rural development and agricultural support',
                education='PhD in Economics from Stanford',
                experience='CEO of Tech Corp (2015-2023), Economic Advisor (2010-2015)'
            ),
            Candidate(
                name='Michael Johnson',
                party='Independent',
                photo_url='/static/images/candidates/michael_johnson.jpg',
                promises='Environmental protection\nTechnology innovation\nTransparent governance',
                assets='Technology patents worth $1,000,000',
                liabilities='No major liabilities',
                background='Environmental activist and tech entrepreneur',
                political_views='Balanced approach with focus on sustainability',
                regional_views='Statewide environmental initiatives',
                education='MS in Environmental Science from MIT',
                experience='Founder of GreenTech Solutions, Environmental Consultant'
            )
        ]
        for candidate in candidates:
            db.session.add(candidate)
        logger.info(f"{len(candidates)} sample candidates created")

    # Create default election
    if Election.query.count() == 0:
        election = Election(
            title='2024 General Election',
            description='Annual general election for selecting representatives',
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True,
            enable_live_results=False
        )
        db.session.add(election)
        logger.info("Default election created")

    db.session.commit()
    logger.info("Sample data initialization complete")
