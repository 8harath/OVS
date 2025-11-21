# Online Voting System (OVS)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.2.5-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Educational-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production--Ready-success.svg)](https://github.com/8harath/OVS)

A comprehensive, secure, and feature-rich online voting platform designed for electronic elections. Built with Flask and modern web technologies, this system demonstrates enterprise-grade security practices while maintaining accessibility for educational and small-scale democratic processes.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Security Features](#security-features)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Known Limitations](#known-limitations)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

---

## Overview

The **Online Voting System (OVS)** is a web-based application that facilitates secure and transparent electronic voting. Originally developed as an educational project, it has evolved into a production-ready platform incorporating industry best practices in web security, user authentication, and database management.

### Purpose

This system addresses the need for accessible, secure, and auditable digital voting solutions suitable for:
- Educational institutions conducting student elections
- Small organizations requiring democratic decision-making tools
- Research and development in e-voting systems
- Learning enterprise-level web application development

### Design Philosophy

The application follows a layered architecture with clear separation of concerns, emphasizing:
- **Security First**: Multiple layers of protection against common web vulnerabilities
- **User Experience**: Intuitive interfaces for voters and administrators
- **Auditability**: Comprehensive logging and vote verification mechanisms
- **Scalability**: Modular design supporting future enhancements
- **Transparency**: Open-source codebase for community review

---

## Key Features

### For Voters

#### Registration & Authentication
- **Comprehensive Registration**: Multi-step registration with personal information collection
- **Identity Verification**: ID document upload with admin verification workflow
- **Age Validation**: Automatic verification of voting eligibility (18+ years)
- **Two-Factor Authentication (2FA)**: Optional TOTP-based MFA for enhanced security
- **Secure Login**: Password hashing with Werkzeug's security utilities
- **Password Recovery**: Token-based secure password reset mechanism

#### Voting Experience
- **One Vote Per Person**: System enforces single vote per election per voter
- **Candidate Profiles**: Comprehensive information including:
  - Political party affiliation
  - Campaign promises
  - Educational background
  - Professional experience
  - Asset and liability declarations
  - Political and regional views
  - Social media links
- **Candidate Comparison**: Side-by-side comparison tool for informed decision-making
- **Vote Confirmation**: Unique reference numbers for vote verification
- **Vote Verification**: Publicly verifiable voting records without compromising ballot secrecy
- **Email Notifications**: Automated confirmations for registration and vote casting

### For Administrators

#### System Management
- **Administrative Dashboard**: Centralized control panel with real-time statistics
- **Voter Management**:
  - Review and approve voter registrations
  - Verify voter eligibility
  - View detailed voter profiles
  - Export voter data to CSV
- **Candidate Management**:
  - Add candidates with photo uploads
  - Edit candidate information
  - Deactivate/remove candidates
  - Manage candidate profiles
- **Election Management**:
  - Create multiple elections
  - Set start and end dates
  - Configure live results display
  - Monitor election status
- **Announcements System**: Post election-related announcements visible to all users

#### Analytics & Reporting
- **Real-time Statistics**:
  - Total registered voters
  - Verified voters
  - Vote turnout percentage
  - Votes per candidate
- **Results Dashboard**: Live election results with visualization
- **Data Export**: CSV export functionality for voters and results
- **Activity Logs**: Comprehensive audit trail of system activities

### API Features

Complete RESTful API for third-party integrations and mobile applications:

- **Health Monitoring**: System health check endpoint
- **Candidate Information**: Retrieve candidate data and details
- **Election Data**: Access election information and status
- **Results Access**: Programmatic access to election results
- **Statistics**: Voting statistics and analytics
- **Vote Verification**: API endpoint for vote verification
- **User Profiles**: Authenticated user data access

---

## System Architecture

### Architectural Pattern

The application employs a **Blueprint-based modular architecture** following the **application factory pattern**, which provides:
- Improved code organization and maintainability
- Better testing capabilities through dependency injection
- Environment-specific configurations
- Scalable structure for feature additions

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  (Jinja2 Templates, HTML5, CSS3, JavaScript)                │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────┬──────────┬──────────┬──────────┐             │
│  │   Auth   │   Main   │  Admin   │   API    │  Blueprints │
│  │ Blueprint│Blueprint │Blueprint │Blueprint │             │
│  └──────────┴──────────┴──────────┴──────────┘             │
│                                                              │
│  ┌──────────────────────────────────────────┐              │
│  │  Middleware (CSRF, Rate Limiting, Auth)  │              │
│  └──────────────────────────────────────────┘              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  (Forms, Validators, Utilities, Decorators)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                    Data Access Layer                         │
│  (SQLAlchemy ORM, Models)                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                    Database Layer                            │
│  (SQLite / PostgreSQL / MySQL)                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Models

The system utilizes five primary database models:

1. **Voter Model**: User accounts with authentication and verification fields
2. **Candidate Model**: Candidate profiles with detailed information
3. **Vote Model**: Vote records with reference numbers and metadata
4. **Election Model**: Election configurations and schedules
5. **Announcement Model**: System-wide announcements

### Request Flow

1. **Client Request** → Web browser or API client
2. **Route Handling** → Blueprint routes process the request
3. **Authentication Check** → Flask-Login verifies user session
4. **CSRF Validation** → Flask-WTF validates form tokens
5. **Rate Limiting** → Flask-Limiter checks request frequency
6. **Business Logic** → Controllers process the request
7. **Database Operations** → SQLAlchemy ORM handles data access
8. **Response Generation** → Jinja2 templates render HTML or JSON
9. **Client Response** → Rendered page or API response

---

## Technology Stack

### Backend Framework
- **Flask 2.2.5**: Lightweight WSGI web application framework
- **Werkzeug 3.1.3**: WSGI utility library for password hashing and security

### Database & ORM
- **SQLAlchemy 3.0.5**: Python SQL toolkit and Object-Relational Mapper
- **SQLite**: Default database (development)
- **PostgreSQL/MySQL**: Recommended for production

### Authentication & Security
- **Flask-Login 0.6.2**: User session management
- **Flask-WTF 1.1.1**: Form handling with CSRF protection
- **Flask-Limiter 3.3.1**: Rate limiting for route protection
- **PyOTP 2.8.0**: Two-factor authentication (TOTP)

### Communication
- **Flask-Mail 0.9.1**: Email integration for notifications

### Data Processing & Visualization
- **Pandas 2.0.3**: Data manipulation and analysis
- **Plotly 5.14.1**: Interactive charts and visualizations

### Utilities
- **python-dotenv 1.0.0**: Environment variable management
- **email-validator 2.0.0**: Email address validation
- **python-dateutil 2.8.2**: Date and time utilities
- **qrcode 7.4.2**: QR code generation for 2FA
- **Pillow 10.0.0**: Image processing

### Testing
- **pytest 7.4.0**: Testing framework
- **pytest-cov 4.1.0**: Code coverage reporting

### Production Server
- **Gunicorn 21.2.0**: Python WSGI HTTP server for UNIX

---

## Prerequisites

Before installing the Online Voting System, ensure your environment meets these requirements:

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Python**: Version 3.8 or higher
- **pip**: Python package installer (usually bundled with Python)
- **Virtual Environment**: Recommended for dependency isolation

### Optional Requirements
- **PostgreSQL or MySQL**: For production deployment
- **Redis**: For distributed rate limiting (production)
- **SMTP Server**: For email notifications
- **Reverse Proxy**: Nginx or Apache for production deployment

### Verify Python Installation
```bash
python3 --version  # Should show Python 3.8 or higher
pip3 --version     # Should show pip version
```

---

## Installation

Follow these steps to set up the Online Voting System on your local machine:

### 1. Clone the Repository

```bash
git clone https://github.com/8harath/OVS.git
cd OVS
```

### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal, indicating the virtual environment is active.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required Python packages specified in `requirements.txt`.

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred text editor
nano .env  # or vim .env, or code .env
```

**Critical configurations to change:**
- `SECRET_KEY`: Generate a strong random key
- `ADMIN_PASSWORD`: Change from default
- `MAIL_USERNAME` and `MAIL_PASSWORD`: Configure for email notifications

### 5. Initialize the Database

```bash
python database.py
```

This script will:
- Create all necessary database tables
- Insert three sample candidates for testing
- Create a default admin account (ADMIN001 / Admin@123)

### 6. Start the Application

**Development Mode:**
```bash
python app.py
```

**Production Mode (using Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 7. Access the Application

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

**Default Admin Credentials:**
- Voter ID: `ADMIN001`
- Password: `Admin@123`

⚠️ **Important**: Change the admin password immediately after first login!

---

## Configuration

The application uses environment variables for configuration, stored in the `.env` file.

### Core Configuration

#### Security Settings
```bash
# Generate a strong secret key (required for session security)
SECRET_KEY=your-generated-secret-key-min-32-characters

# Flask environment (development, production, testing)
FLASK_ENV=production

# Debug mode (NEVER enable in production)
DEBUG=False
```

#### Database Configuration
```bash
# SQLite (default, suitable for development)
DATABASE_URL=sqlite:///voting_system.db

# PostgreSQL (recommended for production)
# DATABASE_URL=postgresql://username:password@localhost:5432/voting_db

# MySQL (alternative for production)
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/voting_db
```

#### Session Security
```bash
# Enable secure cookies (requires HTTPS in production)
SESSION_COOKIE_SECURE=True

# Prevent JavaScript access to session cookies
SESSION_COOKIE_HTTPONLY=True

# CSRF protection for same-site requests
SESSION_COOKIE_SAMESITE=Lax

# Session lifetime in seconds (3600 = 1 hour)
PERMANENT_SESSION_LIFETIME=3600
```

#### Email Configuration

For Gmail:
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=noreply@votingsystem.com
```

**Note**: For Gmail, create an [App Password](https://support.google.com/accounts/answer/185833) instead of using your regular password.

#### Password Policy
```bash
MIN_PASSWORD_LENGTH=8
REQUIRE_UPPERCASE=True
REQUIRE_LOWERCASE=True
REQUIRE_DIGITS=True
REQUIRE_SPECIAL_CHARS=True
```

#### Rate Limiting
```bash
# Memory storage for development
RATELIMIT_STORAGE_URL=memory://

# Redis storage for production (recommended)
# RATELIMIT_STORAGE_URL=redis://localhost:6379

# Default rate limits
RATELIMIT_DEFAULT=200 per day;50 per hour
```

### Generating a Secret Key

Use Python to generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it into your `.env` file.

### Environment-Specific Configurations

The application supports three configuration modes:
- **Development**: Debug enabled, verbose logging
- **Production**: Security hardened, optimized performance
- **Testing**: In-memory database, CSRF disabled

Set the environment using:
```bash
export FLASK_ENV=production  # Linux/macOS
set FLASK_ENV=production     # Windows
```

---

## Usage Guide

### For Voters

#### 1. Registration Process

1. Navigate to the registration page
2. Fill in the registration form:
   - Full name (first and last)
   - Email address
   - Date of birth (must be 18+)
   - Phone number
   - Residential address
   - Create a voter ID (username)
   - Set a secure password (must meet complexity requirements)
   - Upload ID document (PNG, JPG, or PDF)
3. Submit the form
4. Await admin verification (you'll receive an email confirmation)

#### 2. Logging In

1. Go to the login page
2. Enter your voter ID and password
3. If you enabled 2FA, enter the 6-digit code from your authenticator app
4. Check "Remember Me" to stay logged in (optional)

#### 3. Viewing Candidates

- Browse all active candidates from the dashboard
- Click on a candidate to view their detailed profile:
  - Background and education
  - Political views
  - Campaign promises
  - Asset declarations
  - Liability information
  - Social media links

#### 4. Comparing Candidates

- Navigate to the candidate comparison page
- Select multiple candidates to compare side-by-side
- Review their positions on various issues

#### 5. Casting Your Vote

1. Select your preferred candidate
2. Review your choice carefully
3. Click "Cast Vote"
4. Confirm your selection
5. Save your unique reference number for verification

**Important**: You can only vote once per election!

#### 6. Verifying Your Vote

1. Go to the vote verification page
2. Enter your reference number
3. View your vote confirmation (without revealing your choice to others)

### For Administrators

#### Accessing the Admin Panel

1. Log in with admin credentials
2. Click "Admin Panel" in the navigation menu

#### Managing Voter Registrations

1. Go to "Voter Management"
2. View pending registrations
3. Review voter details and uploaded documents
4. Approve or reject registrations
5. Search and filter voters

#### Managing Candidates

1. Navigate to "Candidate Management"
2. Click "Add New Candidate"
3. Fill in candidate information:
   - Name and party affiliation
   - Upload candidate photo
   - Educational background
   - Professional experience
   - Political views
   - Asset and liability information
   - Social media links
4. Save the candidate profile
5. Edit or deactivate candidates as needed

#### Managing Elections

1. Go to "Election Management"
2. Create a new election:
   - Set election title and description
   - Define start and end dates
   - Configure whether to show live results
3. Activate or deactivate elections
4. Monitor election status

#### Viewing Results and Statistics

- **Dashboard**: Overview of total voters, verified voters, and turnout
- **Results Page**: Detailed vote counts per candidate with charts
- **Export Data**: Download voters or results as CSV files

#### Posting Announcements

1. Navigate to "Announcements"
2. Click "Create Announcement"
3. Enter title and content
4. Publish to make it visible to all users

---

## API Documentation

The Online Voting System provides a RESTful API for integration with mobile applications or third-party systems.

### Base URL
```
http://localhost:5000/api/v1
```

### Authentication

Some endpoints require authentication via session cookies. Include credentials in your requests for protected endpoints.

### Endpoints

#### System Health Check

**GET** `/api/v1/health`

Check if the API is operational.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-21T10:30:00Z"
}
```

---

#### Get All Candidates

**GET** `/api/v1/candidates`

Retrieve all active candidates.

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "party": "Progressive Party",
      "photo_url": "/uploads/candidates/photo.jpg",
      "promises": "Education reform and healthcare",
      "background": "Former educator",
      "vote_count": 45
    }
  ],
  "message": "Candidates retrieved successfully",
  "error": null
}
```

---

#### Get Candidate Details

**GET** `/api/v1/candidates/{id}`

Retrieve detailed information about a specific candidate.

**Parameters:**
- `id` (integer): Candidate ID

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "John Doe",
    "party": "Progressive Party",
    "photo_url": "/uploads/candidates/photo.jpg",
    "promises": "Education reform",
    "assets": "Property valued at $200,000",
    "liabilities": "None",
    "background": "Former educator",
    "political_views": "Center-left",
    "regional_views": "Focus on urban development",
    "education": "Master's in Education",
    "experience": "15 years in public service",
    "social_media_links": {
      "twitter": "https://twitter.com/johndoe",
      "facebook": "https://facebook.com/johndoe"
    },
    "vote_count": 45
  },
  "message": "Candidate details retrieved",
  "error": null
}
```

---

#### Get All Elections

**GET** `/api/v1/elections`

Retrieve all elections.

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "National General Election 2025",
      "description": "Presidential and parliamentary elections",
      "start_date": "2025-01-15T00:00:00Z",
      "end_date": "2025-01-15T18:00:00Z",
      "is_active": true,
      "is_ongoing": true
    }
  ],
  "message": "Elections retrieved successfully",
  "error": null
}
```

---

#### Get Election Details

**GET** `/api/v1/elections/{id}`

Retrieve detailed information about a specific election.

**Parameters:**
- `id` (integer): Election ID

---

#### Get Election Results

**GET** `/api/v1/results`

Retrieve current election results.

**Response:**
```json
{
  "data": {
    "total_votes": 150,
    "results": [
      {
        "candidate_id": 1,
        "candidate_name": "John Doe",
        "party": "Progressive Party",
        "vote_count": 75,
        "percentage": 50.0
      }
    ]
  },
  "message": "Results retrieved successfully",
  "error": null
}
```

---

#### Get Voting Statistics

**GET** `/api/v1/statistics`

Retrieve voting statistics.

**Response:**
```json
{
  "data": {
    "total_voters": 300,
    "verified_voters": 280,
    "voted_count": 150,
    "turnout_percentage": 53.57,
    "pending_verification": 20
  },
  "message": "Statistics retrieved successfully",
  "error": null
}
```

---

#### Verify Vote

**GET** `/api/v1/verify-vote/{reference}`

Verify a vote using its reference number.

**Parameters:**
- `reference` (string): Vote reference number

**Response:**
```json
{
  "data": {
    "reference_number": "ABC123DEF456",
    "timestamp": "2025-01-15T12:30:00Z",
    "verified": true
  },
  "message": "Vote verified successfully",
  "error": null
}
```

---

#### Get User Profile

**GET** `/api/v1/profile`

Retrieve the authenticated user's profile.

**Requires**: Authentication

**Response:**
```json
{
  "data": {
    "voter_id": "VTR001",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "has_voted": true,
    "is_verified": true,
    "created_at": "2025-01-01T10:00:00Z"
  },
  "message": "Profile retrieved successfully",
  "error": null
}
```

---

### Error Responses

All endpoints return standardized error responses:

```json
{
  "data": null,
  "message": "Error description",
  "error": "ERROR_CODE"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error

---

## Security Features

Security is a paramount concern for any voting system. OVS implements multiple layers of protection:

### Authentication Security

#### Password Security
- **Hashing**: Werkzeug's `pbkdf2:sha256` with salt
- **Complexity Requirements**: Configurable via environment variables
  - Minimum length (default: 8 characters)
  - Uppercase letters required
  - Lowercase letters required
  - Digits required
  - Special characters required

#### Two-Factor Authentication (2FA)
- **Protocol**: Time-based One-Time Password (TOTP)
- **Standard**: RFC 6238 compliant
- **Implementation**: PyOTP library
- **Setup**: QR code generation for easy authenticator app configuration
- **Optional**: Users can choose to enable 2FA for enhanced security

#### Session Management
- **Secure Cookies**: HTTPOnly flag prevents JavaScript access
- **HTTPS Only**: SESSION_COOKIE_SECURE flag for production
- **SameSite**: Prevents CSRF attacks via third-party websites
- **Expiration**: Configurable session lifetime
- **Logout**: Proper session invalidation

### Protection Against Common Attacks

#### Cross-Site Request Forgery (CSRF)
- **Implementation**: Flask-WTF automatic CSRF tokens
- **Coverage**: All POST, PUT, DELETE requests
- **Validation**: Server-side token verification

#### SQL Injection
- **Prevention**: SQLAlchemy ORM with parameterized queries
- **No Raw SQL**: All database interactions through ORM
- **Input Sanitization**: Automatic escaping of user inputs

#### Cross-Site Scripting (XSS)
- **Prevention**: Jinja2 automatic escaping
- **Content Security Policy**: Recommended in production
- **Input Validation**: Server-side validation of all inputs

#### Brute Force Attacks
- **Rate Limiting**: Flask-Limiter implementation
- **Login Attempts**: 5 attempts per minute per IP
- **Global Limits**: 200 requests per day, 50 per hour
- **Lockout**: Temporary IP blocking after threshold

### Data Security

#### Password Reset
- **Token-Based**: UUID tokens with expiration
- **One-Time Use**: Tokens invalidated after use
- **Time Limit**: 24-hour expiration window
- **Email Verification**: Sent to registered email only

#### File Upload Security
- **Extension Validation**: Whitelist of allowed file types (PNG, JPG, JPEG, PDF)
- **Filename Sanitization**: Werkzeug's `secure_filename()`
- **Unique Filenames**: UUID prefixes prevent conflicts and guessing
- **Size Limits**: Configurable maximum file size (default: 16MB)
- **Storage**: Separate directories for different file types

#### Vote Integrity
- **Reference Numbers**: Unique identifiers for vote verification
- **Metadata Collection**: IP address and user agent logging
- **One Vote Rule**: Database constraints prevent duplicate voting
- **Timestamps**: Accurate vote timing for audit purposes

### Audit & Logging

#### Activity Logging
- **Events Tracked**:
  - User registration
  - Login/logout
  - Vote casting
  - Admin actions
  - Password resets
- **Information Logged**:
  - Timestamp
  - User ID
  - Action type
  - IP address
  - Additional context

#### Error Logging
- **Comprehensive**: All exceptions logged with stack traces
- **Severity Levels**: INFO, WARNING, ERROR, CRITICAL
- **File and Console**: Dual logging for development and production
- **Log File**: `voting_system.log`

### Deployment Security Recommendations

For production environments, implement these additional measures:

1. **HTTPS/TLS**: Use SSL certificates (Let's Encrypt recommended)
2. **Environment Separation**: Never use development config in production
3. **Database Security**: Use strong passwords, limit network access
4. **Firewall**: Configure firewall rules to restrict access
5. **Updates**: Keep all dependencies up to date
6. **Monitoring**: Implement intrusion detection systems
7. **Backups**: Regular encrypted backups of database
8. **DDoS Protection**: Use CDN or DDoS mitigation services
9. **Security Headers**: Implement recommended HTTP security headers
10. **Penetration Testing**: Regular security audits

---

## Testing

The project includes a comprehensive test suite using pytest.

### Running Tests

**Run all tests:**
```bash
pytest
```

**Run with verbose output:**
```bash
pytest -v
```

**Run with coverage report:**
```bash
pytest --cov=. --cov-report=html
```

**Run specific test file:**
```bash
pytest tests/test_auth.py
```

**Run specific test function:**
```bash
pytest tests/test_auth.py::test_registration
```

### Test Coverage

The test suite covers:

- **Authentication Tests** (`test_auth.py`):
  - User registration with valid data
  - Registration with invalid data
  - Login with correct credentials
  - Login with incorrect credentials
  - Logout functionality
  - Password reset request
  - Password reset completion

- **Voting Tests** (`test_voting.py`):
  - Casting a valid vote
  - Preventing double voting
  - Vote verification
  - Vote count accuracy
  - Election status checks

- **API Tests** (`test_api.py`):
  - Health check endpoint
  - Candidate endpoints
  - Election endpoints
  - Results endpoints
  - Statistics endpoints
  - Authentication required endpoints

### Test Fixtures

Located in `tests/conftest.py`, fixtures provide:
- Test application instance
- Test database with sample data
- Authenticated test client
- Admin test client

### Coverage Report

After running tests with coverage, open the HTML report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Writing New Tests

When adding features, create corresponding tests:

1. Create or update test file in `tests/` directory
2. Use existing fixtures from `conftest.py`
3. Follow naming convention: `test_<feature_name>.py`
4. Test both success and failure cases
5. Ensure all tests pass before committing

---

## Project Structure

```
OVS/
├── app.py                      # Application entry point (factory pattern)
├── config.py                   # Configuration management (dev, prod, test)
├── database.py                 # Database initialization script
├── models.py                   # SQLAlchemy database models
├── forms.py                    # WTForms form definitions
├── utils.py                    # Utility functions (email, validation, etc.)
├── decorators.py               # Custom decorators (verified_required, etc.)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── CHANGELOG.md                # Version history and changes
├── IMPROVEMENTS_SUMMARY.md     # Detailed improvements documentation
├── BLOCKCHAIN_INTEGRATION_PLAN.md  # Future enhancement plan
│
├── blueprints/                 # Application blueprints (modular routes)
│   ├── __init__.py             # Blueprint initialization
│   ├── auth.py                 # Authentication routes (login, register, etc.)
│   ├── main.py                 # Main application routes (voting, candidates)
│   ├── admin.py                # Admin panel routes (management features)
│   └── api.py                  # RESTful API routes
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base template with common layout
│   ├── index.html              # Landing page
│   ├── dashboard.html          # User dashboard
│   ├── candidate_detail.html   # Candidate profile page
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── vote_confirmation.html  # Vote confirmation page
│   ├── auth/                   # Authentication-related templates
│   ├── admin/                  # Admin panel templates
│   ├── emails/                 # Email notification templates
│   └── errors/                 # Error pages (403, 404, 429, 500)
│
├── static/                     # Static files (CSS, JavaScript, images)
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   │   └── script.js           # Main JavaScript file
│   └── images/                 # Image assets
│
├── tests/                      # Test suite
│   ├── __init__.py             # Test package initialization
│   ├── conftest.py             # Pytest fixtures and configuration
│   ├── test_auth.py            # Authentication tests
│   ├── test_voting.py          # Voting functionality tests
│   └── test_api.py             # API endpoint tests
│
├── uploads/                    # User-uploaded files (gitignored)
│   ├── candidates/             # Candidate photos
│   └── id_documents/           # Voter ID documents
│
├── database/                   # Database files (gitignored)
│   └── voting_system.db        # SQLite database file
│
└── venv/                       # Virtual environment (gitignored)
```

### Key Files Explained

- **app.py**: Application factory creating Flask app with all extensions
- **config.py**: Environment-based configuration classes
- **models.py**: Database schema definitions (Voter, Candidate, Vote, Election, Announcement)
- **forms.py**: WTForms with validation for all user inputs
- **utils.py**: Helper functions for file handling, email, logging, validation
- **decorators.py**: Custom route decorators for access control

---

## Deployment

### Production Deployment Checklist

Before deploying to production, complete these steps:

#### Security Configuration
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Set `FLASK_ENV=production`
- [ ] Enable `SESSION_COOKIE_SECURE=True` (requires HTTPS)
- [ ] Change default admin password
- [ ] Review and update all environment variables

#### Database Configuration
- [ ] Migrate from SQLite to PostgreSQL or MySQL
- [ ] Configure database backups
- [ ] Set up database connection pooling
- [ ] Optimize database indexes

#### Email Configuration
- [ ] Configure production SMTP server
- [ ] Test email delivery
- [ ] Set up email templates

#### Rate Limiting
- [ ] Configure Redis for distributed rate limiting
- [ ] Adjust rate limits based on expected traffic

#### Infrastructure
- [ ] Set up HTTPS/TLS with valid SSL certificate
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up firewall rules
- [ ] Configure load balancing (if needed)
- [ ] Set up monitoring and alerting

#### Application
- [ ] Set up process manager (systemd, supervisor)
- [ ] Configure logging to external service
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Configure automated backups

### Deployment with Gunicorn and Nginx

#### 1. Install Gunicorn
```bash
pip install gunicorn
```

#### 2. Create Systemd Service

Create `/etc/systemd/system/ovs.service`:

```ini
[Unit]
Description=Online Voting System
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/OVS
Environment="PATH=/path/to/OVS/venv/bin"
ExecStart=/path/to/OVS/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

#### 3. Configure Nginx

Create `/etc/nginx/sites-available/ovs`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/OVS/static;
    }

    location /uploads {
        alias /path/to/OVS/uploads;
    }
}
```

#### 4. Enable and Start Services

```bash
sudo systemctl enable ovs
sudo systemctl start ovs
sudo ln -s /etc/nginx/sites-available/ovs /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

#### 5. Set Up SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Docker Deployment

A sample `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV PORT=8000

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:
```bash
docker build -t ovs .
docker run -d -p 8000:8000 --env-file .env ovs
```

### Cloud Deployment

The application can be deployed to various cloud platforms:

- **Heroku**: Use the provided `Procfile`
- **AWS Elastic Beanstalk**: Package as Python application
- **Google Cloud Run**: Use Docker container
- **Azure App Service**: Deploy via Git or Docker

Refer to platform-specific documentation for detailed instructions.

---

## Known Limitations

### Current Limitations

1. **Frontend Templates**: Some advanced UI components need full implementation
   - Email templates for notifications
   - Enhanced data visualizations
   - Dark mode interface

2. **Scalability**:
   - SQLite not recommended for high-concurrency production use
   - In-memory rate limiting doesn't scale across multiple servers
   - File upload storage limited to local filesystem

3. **Features**:
   - SMS notifications infrastructure not implemented
   - No built-in database migration system
   - Limited multi-language support
   - No built-in backup automation

4. **Authentication**:
   - No OAuth/SSO integration
   - No biometric authentication
   - Limited account recovery options

5. **Accessibility**:
   - WCAG 2.1 compliance not fully verified
   - Screen reader optimization needs enhancement

### Recommendations for Production Use

- **Database**: Migrate to PostgreSQL for production workloads
- **Storage**: Use object storage (S3, Azure Blob) for uploaded files
- **Caching**: Implement Redis or Memcached for performance
- **CDN**: Serve static assets via Content Delivery Network
- **Load Balancing**: Use multiple application servers behind load balancer
- **Monitoring**: Implement comprehensive monitoring and alerting
- **Compliance**: Ensure compliance with local election laws and data protection regulations

---

## Contributing

Contributions to the Online Voting System are welcome! Whether you're fixing bugs, improving documentation, or proposing new features, your help is appreciated.

### How to Contribute

1. **Fork the Repository**
   ```bash
   git clone https://github.com/8harath/OVS.git
   cd OVS
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Write clean, documented code
   - Follow PEP 8 style guidelines
   - Add tests for new features
   - Update documentation as needed

4. **Run Tests**
   ```bash
   pytest
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: Add detailed description of changes"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure all tests pass

### Development Guidelines

#### Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use meaningful variable and function names
- Write docstrings for functions and classes
- Keep functions focused and concise

#### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

#### Testing
- Write tests for all new features
- Maintain or improve code coverage
- Test both success and failure scenarios
- Use descriptive test names

#### Documentation
- Update README if adding new features
- Document API endpoints
- Add inline comments for complex logic
- Update CHANGELOG.md

### Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots if applicable

### Feature Requests

For feature requests:
- Clearly describe the proposed feature
- Explain the use case and benefits
- Consider implementation complexity
- Be open to discussion and feedback

---

## Acknowledgments

This project builds upon the collective knowledge of the open-source community and leverages excellent tools and libraries:

### Core Technologies
- **Flask Framework**: Armin Ronacher and the Pallets team
- **SQLAlchemy**: Mike Bayer and contributors
- **Werkzeug**: Pallets team for security utilities

### Security
- **Flask-Login**: Matthew Frazier and maintainers
- **Flask-WTF**: Dan Jacob and contributors
- **Flask-Limiter**: Ali-Akber Saifee for rate limiting
- **PyOTP**: PyAuth team for 2FA implementation

### Special Thanks
- Educational institutions supporting this project
- Open-source contributors and maintainers
- Security researchers for vulnerability disclosures
- Beta testers and early adopters

### Learning Resources
- Flask documentation and tutorials
- OWASP guidelines for web application security
- Real Python tutorials
- Stack Overflow community

---

## License

This project is developed for educational purposes and is available under an educational license.

**For Educational Use:**
- Free to use for learning and academic projects
- May be used in coursework and presentations
- Suitable for demonstrating web application development skills

**For Commercial or Production Use:**
- Contact the maintainer for licensing arrangements
- Additional security audits recommended
- Compliance with local election laws required

**Disclaimer:**
This system is provided as-is for educational purposes. While security best practices have been implemented, any production deployment should undergo thorough security auditing and compliance review. The maintainers assume no liability for any use of this system in actual elections or voting processes.

---

## Contact & Support

### Project Maintainer
- **GitHub**: [@8harath](https://github.com/8harath)
- **Repository**: [github.com/8harath/OVS](https://github.com/8harath/OVS)

### Getting Help

- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and community support
- **Email**: admin@votingsystem.com (for security vulnerabilities)

### Security Vulnerabilities

If you discover a security vulnerability, please:
1. **DO NOT** open a public issue
2. Email details to admin@votingsystem.com
3. Include steps to reproduce
4. Allow reasonable time for response before public disclosure

---

## Project Status

**Current Version**: 2.0.0
**Status**: Production-Ready Backend | Frontend Templates In Progress
**Last Updated**: November 2025

### Recent Updates
- ✅ Complete backend implementation with enterprise security features
- ✅ RESTful API for third-party integrations
- ✅ Comprehensive test suite
- ✅ Modular blueprint architecture
- 🔨 Frontend UI enhancements in progress

### Roadmap

**Short Term:**
- Complete frontend template implementations
- Enhanced data visualizations
- Improved mobile responsiveness

**Medium Term:**
- Blockchain integration for vote immutability
- Multi-language support
- Advanced analytics dashboard

**Long Term:**
- Biometric authentication
- Mobile native applications
- Real-time collaboration features

For detailed enhancement proposals, see [ENHANCEMENTS.md](ENHANCEMENTS.md).

---

**Built with ❤️ for secure and transparent democratic processes**
