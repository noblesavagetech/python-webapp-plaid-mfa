# Technical Specifications for Python-Webapp

## Overview
The Python-Webapp is a Flask-based web application for FinTech services with optional two-factor authentication (2FA). Users must complete email verification during registration. SMS-based 2FA via Vonage Verify API is available for users who want enhanced security. The application uses PostgreSQL for data storage and is containerized using Docker with Railway deployment support.

---

## Key Features
- **User Registration**: Account creation with email and password.
- **Email Verification**: Mandatory 6-digit code verification via Brevo (SendinBlue) during signup.
- **Optional Two-Factor Authentication**: Users can enable SMS-based 2FA for enhanced security.
- **Session-Based Authentication**: Secure user sessions managed by Flask-Login.
- **PostgreSQL Database**: Secure storage for user credentials and optional phone numbers.
- **Transactional SMS**: TCPA-compliant SMS delivery via Vonage Verify API for 2FA.
- **Vonage Verify API**: Purpose-built 2FA service with automatic voice fallback if SMS fails.

---

## Authentication Flow

### New User Registration
1. **Signup**: User provides email and password
2. **Email Verification**: System sends 6-digit code via Brevo → User enters code
3. **Account Activated**: User can access dashboard
4. **Optional 2FA**: User can choose to enable SMS 2FA from dashboard

### Returning User Login (Without 2FA)
1. **Credentials**: User enters email and password
2. **Access Granted**: User authenticated and logged in

### Returning User Login (With 2FA Enabled)
1. **Credentials**: User enters email and password
2. **SMS Challenge**: System sends 6-digit code via Vonage to registered phone
3. **Verification**: User enters SMS code
4. **Access Granted**: User authenticated and logged in

### User Identity
Each user account consists of:
- **Email** (unique identifier for login) - Required
- **Password** (hashed with Werkzeug) - Required
- **Email Verification Status** (boolean flag) - Required for access
- **Phone Number** (E.164 format) - Optional, required only if 2FA enabled
- **MFA Enabled Status** (boolean flag) - Optional, user choice
- **Vonage Request ID** (temporary, cleared after verification) - Only during 2FA verification

---

## Technical Components

### 1. Web Framework
- **Flask**: Web framework for routing and application logic.
- **Flask-Login**: Session-based user authentication.
- **Flask-SQLAlchemy**: ORM for database interactions.
- **Flask-Migrate**: Database migrations.

### 2. Database
- **PostgreSQL**: Primary database for storing application data.
- **SQLAlchemy**: ORM for database queries.
- **Psycopg2**: PostgreSQL adapter for Python.

### 3. Communication Services
- **Vonage (Nexmo)**: SMS delivery for 2FA verification codes via Verify API.
- **Brevo (SendinBlue)**: Transactional email delivery for account verification.

### 4. Environment Management
- **Python-Dotenv**: Manages environment variables.

### 5. Validation
- **Email-Validator**: Validates email addresses during registration.

### 6. Deployment
- **Gunicorn**: WSGI HTTP server for production.
- **Docker**: Containerization for consistent environments.
- **Docker Compose**: Orchestrates multi-container setups.
- **Railway**: Cloud deployment platform.

---

## Deployment Details

### Dockerfile
- **Base Image**: Python 3.11-slim.
- **Dependencies**: System dependencies (e.g., `gcc`, `postgresql-client`) and Python packages from `requirements.txt`.
- **Environment Variables**:
  - `FLASK_APP=app.py`
  - `PYTHONUNBUFFERED=1`
- **Command**: Runs the app using Gunicorn with 4 workers.

### Docker Compose
- **Services**:
  - `web`: Flask application.
  - `db`: PostgreSQL database.
- **Volumes**:
  - `postgres_data`: Persistent storage for database.
- **Ports**:
  - `5000:5000` (web service).
  - `5432:5432` (database).

### Railway Deployment
- **Environment Variables**:
  - `FLASK_ENV=production`
  - `SECRET_KEY`: Application secret key.
  - `DATABASE_URL`: PostgreSQL connection string.
  - `BREVO_API_KEY`: Brevo API key for email delivery.
  - `SENDER_EMAIL`, `SENDER_NAME`: Email sender configuration.
  - `VONAGE_API_KEY`, `VONAGE_API_SECRET`: Vonage credentials for SMS.
  - `VONAGE_BRAND_NAME`: Brand name displayed in SMS messages.
- **Steps**:
  1. Connect GitHub repository.
  2. Add PostgreSQL database.
  3. Configure environment variables.

---

## Security Policies
- **Email Verification**: Required for all accounts before dashboard access.
- **Optional 2FA**: Users can enable SMS-based two-factor authentication for enhanced security.
- **Login Verification**: Users with 2FA enabled must enter SMS code via Vonage Verify API at login.
- **Password Security**: Secure hashing with Werkzeug's `generate_password_hash`.
- **Session Management**: Flask-Login handles secure session cookies with httponly and samesite flags.
- **SMS Compliance**: Transactional SMS only for 2FA verification (non-marketing, TCPA compliant).
- **User Consent**: Phone numbers only collected when users opt-in to 2FA with clear security purpose.
- **Data Protection**: HTTPS for communication, encrypted database backups.
- **Input Validation**: Email validation with `email-validator`, phone number E.164 format enforcement.
- **Request ID Cleanup**: Vonage request IDs cleared immediately after successful verification.

---

## Monitoring and Maintenance
- **Logging**: Tracks user actions and API usage.
- **Incident Response**: Defined plan for security breaches.
- **Backup and Recovery**: Regular database backups and recovery testing.
- **Updates**: Regular dependency updates and security patching.

---

## Roles and Responsibilities
- **Developers**: Implement features and fix vulnerabilities.
- **Administrators**: Monitor systems and enforce policies.
- **Users**: Follow security guidelines and report issues.

---

## References
- **Documentation**:
  - [Flask](https://flask.palletsprojects.com/)
  - [SQLAlchemy](https://www.sqlalchemy.org/)
  - [Vonage Verify API](https://developer.vonage.com/en/verify/overview)
  - [Brevo (SendinBlue)](https://developers.brevo.com/)
- **Deployment**:
  - [Docker](https://www.docker.com/)
  - [Railway](https://railway.app/)

---

**Last Updated**: December 31, 2025
