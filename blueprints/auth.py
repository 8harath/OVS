# blueprints/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, Voter
from forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm, MFASetupForm
from utils import save_file, send_registration_email, send_password_reset_email, log_activity
import pyotp
import qrcode
import io
import base64
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Handle file upload
            id_document_path = None
            if form.id_document.data:
                id_document_path = save_file(form.id_document.data, 'id_documents')

            # Create new voter
            voter = Voter(
                name=form.name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                date_of_birth=form.date_of_birth.data,
                phone_number=form.phone_number.data,
                address=form.address.data,
                voter_id=form.voter_id.data.upper(),
                id_document_path=id_document_path
            )
            voter.set_password(form.password.data)

            db.session.add(voter)
            db.session.commit()

            # Send registration email
            send_registration_email(voter)
            log_activity(voter.id, 'REGISTERED', f'New voter registered: {voter.voter_id}')

            flash('Registration successful! Please wait for admin verification before you can vote.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'error')

    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        voter = Voter.query.filter_by(voter_id=form.voter_id.data.upper()).first()

        if voter and voter.check_password(form.password.data):
            # Check MFA if enabled
            if voter.mfa_enabled:
                if not form.mfa_code.data:
                    flash('Please enter your 2FA code.', 'warning')
                    return render_template('auth/login.html', form=form, show_mfa=True)

                totp = pyotp.TOTP(voter.mfa_secret)
                if not totp.verify(form.mfa_code.data):
                    flash('Invalid 2FA code.', 'error')
                    return render_template('auth/login.html', form=form, show_mfa=True)

            login_user(voter, remember=form.remember_me.data)
            log_activity(voter.id, 'LOGIN', 'User logged in successfully')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid voter ID or password.', 'error')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'LOGOUT', 'User logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        voter = Voter.query.filter_by(email=form.email.data).first()
        if voter:
            token = voter.generate_reset_token()
            db.session.commit()

            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_password_reset_email(voter, reset_url)
            log_activity(voter.id, 'PASSWORD_RESET_REQUEST', 'Password reset requested')

        # Always show success message to prevent email enumeration
        flash('If your email is registered, you will receive password reset instructions.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_request.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    voter = Voter.query.filter_by(reset_token=token).first()
    if not voter or not voter.verify_reset_token(token):
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.reset_password_request'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        voter.set_password(form.password.data)
        voter.reset_token = None
        voter.reset_token_expiry = None
        db.session.commit()

        log_activity(voter.id, 'PASSWORD_RESET', 'Password reset successful')
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/setup-mfa', methods=['GET', 'POST'])
@login_required
def setup_mfa():
    if current_user.mfa_enabled:
        flash('Two-factor authentication is already enabled.', 'info')
        return redirect(url_for('main.dashboard'))

    form = MFASetupForm()

    # Generate secret if not exists
    if not current_user.mfa_secret:
        current_user.mfa_secret = pyotp.random_base32()
        db.session.commit()

    # Generate QR code
    totp = pyotp.TOTP(current_user.mfa_secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user.email,
        issuer_name='Online Voting System'
    )

    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_code_base64 = base64.b64encode(buf.getvalue()).decode()

    if form.validate_on_submit():
        if totp.verify(form.verification_code.data):
            current_user.mfa_enabled = True
            db.session.commit()
            log_activity(current_user.id, 'MFA_ENABLED', '2FA enabled')
            flash('Two-factor authentication has been enabled successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid verification code. Please try again.', 'error')

    return render_template('auth/setup_mfa.html', form=form, qr_code=qr_code_base64)

@auth_bp.route('/disable-mfa', methods=['POST'])
@login_required
def disable_mfa():
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    db.session.commit()
    log_activity(current_user.id, 'MFA_DISABLED', '2FA disabled')
    flash('Two-factor authentication has been disabled.', 'info')
    return redirect(url_for('main.dashboard'))
