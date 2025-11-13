# Online Voting System

A secure, feature-rich online voting platform built with Flask. This system provides comprehensive election management capabilities with enterprise-grade security features.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Security Features](#security-features)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## Features

### Core Voting Features
- **Secure Voter Registration**: Complete registration with email verification and document upload
- **Authentication**: Secure login with password hashing and optional 2FA
- **One-Time Voting**: Each voter can cast only one vote per election
- **Vote Verification**: Verify votes using unique reference numbers
- **Real-time Results**: Live election results dashboard with charts
- **Candidate Profiles**: Detailed candidate information including promises, background, assets, and liabilities
- **Candidate Comparison**: Side-by-side comparison of multiple candidates

### Admin Features
- **Complete Admin Panel**: Manage voters, candidates, elections, and announcements
- **Voter Management**: Approve/reject voter registrations, view voter details
- **Candidate Management**: Add, edit, delete candidates with photo uploads
- **Election Management**: Create and manage multiple elections
- **Results Export**: Export voters and results to CSV
- **Real-time Statistics**: View voter turnout and election statistics

### Security Features
- **Password Security**: Enforced password complexity requirements
- **CSRF Protection**: All forms protected against CSRF attacks
- **Rate Limiting**: Prevents brute force attacks (5 login attempts per minute)
- **Session Security**: Secure, HTTPOnly cookies with configurable lifetime
- **Input Validation**: Comprehensive form validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **Two-Factor Authentication (2FA)**: Optional TOTP-based MFA
- **Password Reset**: Secure token-based password recovery

### Additional Features
- **Email Notifications**: Registration confirmations, vote confirmations, password resets
- **RESTful API**: Complete API for mobile app integration
- **Voter Eligibility**: Age verification (18+), address validation, ID document upload
- **Announcements System**: Admin can post election-related announcements
- **Error Handling**: Custom error pages (403, 404, 429, 500)
- **Logging**: Comprehensive activity logging
- **Responsive Design**: Mobile-friendly interface

## Technology Stack

- **Backend**: Flask 2.2.5
- **Database**: SQLAlchemy ORM with SQLite (easily changeable to PostgreSQL/MySQL)
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with CSRF protection
- **Security**: Werkzeug password hashing, Flask-Limiter
- **Email**: Flask-Mail
- **2FA**: PyOTP with QR code generation
- **Testing**: Pytest with coverage
- **Visualization**: Plotly (for charts)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/8harath/Online-Voting-System.git
   cd Online-Voting-System
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example env file
   cp .env.example .env

   # Edit .env and configure your settings
   # At minimum, change the SECRET_KEY
   ```

5. **Initialize the database**
   ```bash
   python database.py
   ```

   This will create:
   - Database tables
   - Sample candidates
   - Default admin user (ADMIN001 / Admin@123)

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open your browser and navigate to: `http://127.0.0.1:5000`
   - Login with admin credentials: `ADMIN001` / `Admin@123`

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Security
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=False

# Database
DATABASE_URL=sqlite:///voting_system.db

# Email (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password

# Admin
ADMIN_EMAIL=admin@votingsystem.com
ADMIN_PASSWORD=Admin@123

# Password Policy
MIN_PASSWORD_LENGTH=8
REQUIRE_UPPERCASE=True
REQUIRE_LOWERCASE=True
REQUIRE_DIGITS=True
REQUIRE_SPECIAL_CHARS=True
```

### Database Reset

To reset the database and start fresh:

```bash
python database.py --reset
```

**Warning**: This will delete all data!

## Usage

### For Voters

1. **Register**: Create an account with your details and upload ID document
2. **Wait for Verification**: Admin must verify your account
3. **Login**: Use your Voter ID and password
4. **View Candidates**: Browse candidate profiles and compare them
5. **Cast Vote**: Select a candidate and cast your vote
6. **Get Confirmation**: Save your reference number
7. **Verify Vote**: Use reference number to verify your vote later

### For Administrators

1. **Login**: Use admin credentials (ADMIN001 / Admin@123)
2. **Access Admin Panel**: Click "Admin Panel" in navigation
3. **Manage Voters**: Approve registrations, view voter details
4. **Manage Candidates**: Add/edit/delete candidates
5. **Manage Elections**: Create and configure elections
6. **View Results**: Access real-time results and statistics
7. **Export Data**: Download voters and results as CSV

## API Documentation

### Base URL
```
http://localhost:5000/api/v1
```

### Endpoints

#### Health Check
```
GET /api/v1/health
```

#### Candidates
```
GET /api/v1/candidates              # Get all candidates
GET /api/v1/candidates/{id}         # Get candidate details
```

#### Elections
```
GET /api/v1/elections               # Get all elections
GET /api/v1/elections/{id}          # Get election details
```

#### Results
```
GET /api/v1/results                 # Get election results
```

#### Statistics
```
GET /api/v1/statistics              # Get voting statistics
```

#### Vote Verification
```
GET /api/v1/verify-vote/{reference} # Verify a vote
```

#### User Profile (Authenticated)
```
GET /api/v1/profile                 # Get current user profile
```

All API responses follow this format:
```json
{
  "data": {...},
  "message": "Success message",
  "error": null
}
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

Test coverage includes:
- Authentication (registration, login, logout)
- Voting (casting votes, preventing double voting)
- API endpoints
- Password reset
- Admin functions

## Security Features

### Implemented Security Measures

1. **Authentication Security**
   - Password hashing with Werkzeug
   - Password complexity requirements
   - Optional 2FA with TOTP
   - Secure session management

2. **Protection Against Attacks**
   - CSRF protection on all forms
   - Rate limiting (5 login attempts/min)
   - SQL injection prevention (SQLAlchemy ORM)
   - XSS protection (template escaping)

3. **Data Security**
   - Secure password reset with tokens
   - HTTPOnly, Secure cookies
   - Input validation on all forms
   - File upload restrictions

4. **Audit & Logging**
   - Activity logging for all actions
   - Error logging
   - Vote tracking with IP and user agent

## Project Structure

```
OVS/
├── app.py                  # Main application file
├── config.py               # Configuration management
├── database.py             # Database initialization
├── models.py               # SQLAlchemy models
├── forms.py                # WTForms definitions
├── utils.py                # Utility functions
├── decorators.py           # Custom decorators
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── .gitignore             # Git ignore file
│
├── blueprints/            # Application blueprints
│   ├── __init__.py
│   ├── auth.py            # Authentication routes
│   ├── main.py            # Main routes
│   ├── admin.py           # Admin routes
│   └── api.py             # API routes
│
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── auth/              # Auth templates
│   ├── admin/             # Admin templates
│   ├── emails/            # Email templates
│   └── errors/            # Error pages
│
├── static/                # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── tests/                 # Test files
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_voting.py
│   └── test_api.py
│
└── uploads/               # User uploads
    ├── candidates/
    └── id_documents/
```

## Default Credentials

**Admin Account:**
- Voter ID: `ADMIN001`
- Password: `Admin@123`

**Sample Candidates:** Three pre-loaded candidates for testing

**Important:** Change the admin password after first login!

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Ensure all tests pass before submitting PR

## License

This project is created for educational purposes.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: admin@votingsystem.com

## Acknowledgments

- Flask framework and its extensions
- All contributors and testers
- Educational institutions supporting this project

---

**Note**: This is a college project showcasing web application development skills. For production use, additional security measures and infrastructure considerations would be required.
