# Changelog

All notable changes to the Online Voting System project are documented here.

## [2.0.0] - 2025-11-13

### Major Refactoring & Feature Additions

This release represents a complete overhaul of the Online Voting System with enterprise-grade features and security improvements.

### Added

#### Security Features
- **CSRF Protection**: All forms now protected against CSRF attacks using Flask-WTF
- **Rate Limiting**: Implemented Flask-Limiter to prevent brute force attacks (5 login attempts per minute)
- **Password Security**: Enforced password complexity requirements (min 8 chars, uppercase, lowercase, digits, special chars)
- **Two-Factor Authentication**: Optional TOTP-based 2FA with QR code setup
- **Secure Session Management**: HTTPOnly, secure cookies with configurable lifetime
- **Password Reset**: Secure token-based password recovery system
- **Input Validation**: Comprehensive validation for all form inputs

#### Authentication & User Management
- Email-based user registration with verification
- Age validation (18+ requirement)
- Address collection and validation
- ID document upload during registration
- Phone number validation
- Voter verification workflow (admin approval required)
- MFA setup and management

#### Admin Features
- Complete admin dashboard with statistics
- Voter management (approve, verify, delete voters)
- Candidate management (add, edit, delete with photo uploads)
- Election management (create and configure multiple elections)
- Announcements system
- Results export to CSV
- Voter data export to CSV
- Real-time statistics and analytics

#### Voting Features
- Vote verification system with reference numbers
- Candidate comparison tool (side-by-side comparison)
- Election results dashboard with visualizations
- Live results option (configurable)
- Vote confirmation with email notifications
- IP address and user agent tracking for votes

#### API Features
- RESTful API for mobile integration
- Endpoints for candidates, elections, results, statistics
- Vote verification API
- User profile API
- Admin statistics API
- Standardized JSON response format
- API health check endpoint

#### Technical Improvements
- **SQLAlchemy ORM**: Replaced raw SQL with SQLAlchemy for better security and maintainability
- **Blueprint Architecture**: Organized code into modular blueprints (auth, main, admin, api)
- **Configuration Management**: Environment-based configuration with .env support
- **Error Handling**: Custom error pages (403, 404, 429, 500)
- **Logging**: Comprehensive activity and error logging
- **Email System**: Flask-Mail integration for notifications
- **File Uploads**: Secure file upload system for candidates and ID documents

#### Testing
- Pytest test suite with fixtures
- Authentication tests
- Voting functionality tests
- API endpoint tests
- Test coverage reporting

#### Documentation
- Comprehensive README with setup instructions
- API documentation
- Security features documentation
- Project structure documentation
- Contributing guidelines
- Environment configuration examples

### Changed

#### Database
- Migrated from raw SQLite queries to SQLAlchemy ORM
- Enhanced voter model with email, address, verification status, MFA fields
- Enhanced candidate model with education, experience, social media links
- Added Election model for managing multiple elections
- Added Announcement model
- Improved database relationships and foreign keys
- Database initialization script with sample data

#### Application Structure
- Refactored monolithic app.py into modular blueprints
- Created separate modules for forms, models, utils, decorators
- Implemented application factory pattern
- Improved code organization and separation of concerns

#### User Interface
- Note: Backend fully implemented; frontend templates need creation
- Template structure prepared for enhanced UI
- Error pages framework in place

#### Configuration
- Moved from hardcoded config to environment variables
- Created development, production, and testing configurations
- Secure secret key management
- Configurable email, database, and security settings

### Security Improvements

1. **Eliminated Critical Vulnerabilities**
   - Removed hardcoded secret key
   - Disabled debug mode in production
   - Fixed SQL injection risks with ORM
   - Added CSRF protection
   - Implemented rate limiting

2. **Enhanced Authentication**
   - Strong password requirements
   - Optional 2FA
   - Secure password reset
   - Session security

3. **Input Validation**
   - Form-level validation
   - Email validation
   - Phone number validation
   - Age verification
   - File upload restrictions

4. **Audit Trail**
   - Activity logging
   - Vote tracking with metadata
   - Error logging

### Dependencies

#### New Dependencies Added
- Flask-SQLAlchemy (ORM)
- Flask-WTF (forms and CSRF)
- Flask-Login (authentication)
- Flask-Limiter (rate limiting)
- Flask-Mail (email)
- python-dotenv (environment variables)
- email-validator (email validation)
- python-dateutil (date utilities)
- pyotp (2FA)
- qrcode (QR code generation)
- Pillow (image processing)
- plotly (charts)
- pandas (data processing)
- pytest (testing)
- pytest-cov (test coverage)

### File Structure Changes

```
New files added:
- config.py (configuration management)
- forms.py (WTForms definitions)
- utils.py (utility functions)
- decorators.py (custom decorators)
- .env.example (environment template)
- .gitignore (git ignore rules)
- CHANGELOG.md (this file)
- blueprints/ (modular routes)
  - auth.py
  - main.py
  - admin.py
  - api.py
- tests/ (test suite)
  - conftest.py
  - test_auth.py
  - test_voting.py
  - test_api.py
```

### Migration Notes

For users upgrading from v1.x:

1. Install new dependencies: `pip install -r requirements.txt`
2. Create .env file from .env.example
3. Run database migration: `python database.py`
4. Update any custom templates to use new blueprint routes

### Breaking Changes

- URL routes changed due to blueprint implementation
  - `/login` → `/auth/login`
  - `/register` → `/auth/register`
  - Admin routes now prefixed with `/admin/`
- Database schema significantly changed (requires fresh database)
- Configuration moved to environment variables

### Known Issues

- HTML templates need to be created/updated for new features
- Email templates for notifications need implementation
- Charts and visualizations need frontend implementation
- Dark mode UI not yet implemented
- SMS notifications infrastructure not implemented

### Future Enhancements

- Blockchain integration for vote immutability
- Enhanced data visualizations
- Mobile app development
- Biometric authentication
- Multi-language support
- Accessibility improvements (WCAG compliance)
- Performance optimizations
- Database migration to PostgreSQL for production

---

## [1.0.0] - Initial Release

### Added
- Basic voter registration
- Simple login/logout
- Candidate viewing
- Basic voting functionality
- Vote confirmation
- SQLite database with raw queries

### Security Issues (Fixed in 2.0.0)
- Hardcoded secret key
- No CSRF protection
- No rate limiting
- Weak password requirements
- SQL injection vulnerabilities
- No input validation
