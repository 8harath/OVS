# decorators.py
from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def verified_required(f):
    """Decorator to require verified voter status"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_verified:
            flash('Your account is not verified. Please contact the administrator.', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def not_voted_required(f):
    """Decorator to check if user has not voted yet"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if current_user.has_voted:
            flash('You have already cast your vote.', 'info')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
