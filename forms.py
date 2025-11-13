# forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, DateField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from models import Voter
import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class PasswordValidator:
    """Custom password validator"""
    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True,
                 require_digits=True, require_special=True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special

    def __call__(self, form, field):
        password = field.data
        if len(password) < self.min_length:
            raise ValidationError(f'Password must be at least {self.min_length} characters long.')

        if self.require_uppercase and not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')

        if self.require_lowercase and not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')

        if self.require_digits and not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one digit.')

        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character.')

class AgeValidator:
    """Validator to check if user is at least 18 years old"""
    def __init__(self, min_age=18):
        self.min_age = min_age

    def __call__(self, form, field):
        if field.data:
            today = date.today()
            age = relativedelta(today, field.data).years
            if age < self.min_age:
                raise ValidationError(f'You must be at least {self.min_age} years old to register.')

class RegistrationForm(FlaskForm):
    name = StringField('First Name',
                      validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    date_of_birth = DateField('Date of Birth',
                             format='%Y-%m-%d',
                             validators=[DataRequired(), AgeValidator(min_age=18)])
    phone_number = StringField('Phone Number',
                              validators=[DataRequired(),
                                        Regexp(r'^\+?1?\d{9,15}$',
                                             message='Invalid phone number format.')])
    address = TextAreaField('Address',
                          validators=[DataRequired(), Length(min=10, max=500)])
    voter_id = StringField('Voter ID',
                          validators=[DataRequired(),
                                    Length(min=5, max=50),
                                    Regexp(r'^[A-Z0-9]+$',
                                         message='Voter ID must contain only uppercase letters and numbers.')])
    password = PasswordField('Password',
                           validators=[DataRequired(), PasswordValidator()])
    confirm_password = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password')])
    id_document = FileField('ID Document (PDF, PNG, JPG)',
                           validators=[FileAllowed(['pdf', 'png', 'jpg', 'jpeg'],
                                                  'Only PDF and image files allowed.')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        voter = Voter.query.filter_by(email=email.data).first()
        if voter:
            raise ValidationError('Email already registered. Please use a different email.')

    def validate_voter_id(self, voter_id):
        voter = Voter.query.filter_by(voter_id=voter_id.data).first()
        if voter:
            raise ValidationError('Voter ID already exists. Please use a different ID.')

class LoginForm(FlaskForm):
    voter_id = StringField('Voter ID',
                          validators=[DataRequired()])
    password = PasswordField('Password',
                           validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    mfa_code = StringField('2FA Code (if enabled)',
                          validators=[Length(max=6)])
    submit = SubmitField('Login')

class VoteForm(FlaskForm):
    submit = SubmitField('Cast Vote')

class CandidateForm(FlaskForm):
    name = StringField('Candidate Name',
                      validators=[DataRequired(), Length(min=2, max=100)])
    party = StringField('Party Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    photo = FileField('Candidate Photo',
                     validators=[FileAllowed(['png', 'jpg', 'jpeg'], 'Images only!')])
    promises = TextAreaField('Election Promises',
                           validators=[DataRequired()])
    assets = TextAreaField('Assets',
                          validators=[DataRequired()])
    liabilities = TextAreaField('Liabilities',
                              validators=[DataRequired()])
    background = TextAreaField('Background',
                             validators=[DataRequired()])
    political_views = TextAreaField('Political Views',
                                   validators=[DataRequired()])
    regional_views = TextAreaField('Regional Views',
                                  validators=[DataRequired()])
    education = TextAreaField('Education')
    experience = TextAreaField('Experience')
    submit = SubmitField('Add Candidate')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password',
                           validators=[DataRequired(), PasswordValidator()])
    confirm_password = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class VerifyVoteForm(FlaskForm):
    reference_number = StringField('Reference Number',
                                  validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Verify Vote')

class MFASetupForm(FlaskForm):
    verification_code = StringField('Verification Code',
                                   validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Enable 2FA')

class ElectionForm(FlaskForm):
    title = StringField('Election Title',
                       validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description')
    start_date = DateField('Start Date',
                          format='%Y-%m-%d',
                          validators=[DataRequired()])
    end_date = DateField('End Date',
                        format='%Y-%m-%d',
                        validators=[DataRequired()])
    is_active = BooleanField('Active')
    enable_live_results = BooleanField('Enable Live Results')
    submit = SubmitField('Create Election')

class AnnouncementForm(FlaskForm):
    title = StringField('Announcement Title',
                       validators=[DataRequired(), Length(min=5, max=200)])
    content = TextAreaField('Content',
                          validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Post Announcement')
