# BBA Services - Flask App with Email Verification & MFA

A Flask web application for business financial health assessment featuring secure email verification and two-factor authentication (TOTP-based MFA).

## ✨ Features

- 🔐 **Secure Authentication**: Email verification + TOTP-based MFA
- 📧 **Email Integration**: Brevo HTTP API for reliable email delivery  
- 🏛️ **Production Ready**: PostgreSQL database with SQLite fallback
- 🚀 **Railway Deployment**: Optimized for cloud deployment
- 🔒 **Security First**: PBKDF2 password hashing, JWT tokens, secure sessions
- 📱 **Mobile Friendly**: Responsive design with modern UI

## 🔄 User Flow

1. **Sign Up** → Enter email & password
2. **Email Verification** → Receive 6-digit code via email  
3. **MFA Setup** → Scan QR code with authenticator app
4. **Login** → Email + password + TOTP code
5. **Dashboard** → Access secured features

## 🏗️ Architecture

- **Framework**: Flask with application factory pattern
- **Database**: PostgreSQL (production) / SQLite (development)  
- **Authentication**: Flask-Login + custom TOTP implementation
- **Email**: Brevo HTTP API (Railway SMTP-port restrictions)
- **Migrations**: Flask-Migrate for database schema management
- **Deployment**: Gunicorn WSGI server

## 🚀 Quick Start

### Local Development

```bash
# Clone and install
git clone https://github.com/noblesavagetech/python-webapp-plaid-mfa.git
cd python-webapp-plaid-mfa
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Edit .env with your configuration

# Run development server
python app.py
```

### Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# Configure environment variables in Railway dashboard:
# DATABASE_URL (auto-configured with Railway PostgreSQL)
# SECRET_KEY (generate secure key)
# JWT_SECRET_KEY (generate secure key)  
# BREVO_API_KEY (from Brevo account)
# SENDER_EMAIL (verified sender email)
# SENDER_NAME (display name for emails)

# Deploy
railway up
```

## 🔧 Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
BREVO_API_KEY=your-brevo-api-key
SENDER_EMAIL=noreply@yourdomain.com

# Optional  
SENDER_NAME="BBA Services"
APP_URL=https://your-app.railway.app
TOKEN_EXPIRATION=86400
FLASK_ENV=production
```

## 📁 Project Structure

```
├── app.py                 # Application factory & entry point
├── requirements.txt       # Python dependencies
├── Procfile              # Railway deployment config
├── railway.json          # Railway build settings
├── app/
│   ├── models.py         # User model with MFA support
│   ├── config.py         # Application configuration
│   ├── routes/
│   │   ├── auth.py       # Authentication routes
│   │   └── main.py       # Main application routes
│   ├── utils/
│   │   └── email.py      # Email sending utilities
│   ├── templates/        # Jinja2 HTML templates
│   └── static/           # CSS & JavaScript assets
├── migrations/           # Database migration files
```

## 🛡️ Security Features

- **Password Security**: PBKDF2 hashing with salt
- **Session Security**: HTTPOnly, Secure, SameSite cookies  
- **Email Verification**: 6-digit codes with expiration
- **TOTP MFA**: RFC6238-compliant time-based codes
- **CSRF Protection**: Built-in Flask-Login protection
- **Input Validation**: Email validation & sanitization

## 📋 Database Schema

```sql
-- Users table with MFA support
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    totp_secret VARCHAR(255),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(6),
    created_at TIMESTAMP DEFAULT NOW(),
    verified_at TIMESTAMP
);
```

## 🔍 API Endpoints

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Landing page |
| `/signup` | GET/POST | User registration |
| `/login` | GET/POST | User login |
| `/verify-email` | GET/POST | Email verification |
| `/setup-mfa` | GET/POST | MFA setup |
| `/dashboard` | GET | Protected dashboard |
| `/logout` | GET | User logout |
| `/resend-verification` | GET | Resend verification code |

## 🧪 Testing

```bash
# Run application tests
python -c "import app; print('✅ App imports successfully')"

# Test email configuration (requires valid BREVO_API_KEY)
python -c "from app.utils.email import send_verification_email; print('✅ Email module loaded')"

# Check database connectivity
python -c "from app import create_app; app=create_app(); print('✅ Database connection OK')"
```

## 📝 Migration Commands

```bash
# Initialize migrations (first time only)
export FLASK_APP=app.py
flask db init

# Create migration for schema changes
flask db migrate -m "Add MFA fields"

# Apply migrations
flask db upgrade

# Railway deployment (automatic)
# Migrations run automatically via Procfile: flask db upgrade && gunicorn app:app
```

## 🚨 Production Checklist

- ✅ Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- ✅ Configure PostgreSQL database via `DATABASE_URL`
- ✅ Set up Brevo account with verified sender email
- ✅ Enable HTTPS/SSL (automatic on Railway)
- ✅ Configure proper `CORS_ORIGINS` if needed
- ✅ Monitor application logs and performance
- ✅ Set up automated backups for database
- ✅ Test email delivery in production environment

## 🐛 Troubleshooting

**App won't start:**
- Check that all required environment variables are set
- Verify database connection string format
- Ensure Python dependencies are installed

**Emails not sending:**
- Verify `BREVO_API_KEY` is correct
- Check `SENDER_EMAIL` is verified in Brevo
- Review application logs for API errors

**Database errors:**  
- Ensure PostgreSQL is running and accessible
- Run `flask db upgrade` to apply pending migrations
- Check `DATABASE_URL` format: `postgresql://user:pass@host:port/db`

**MFA issues:**
- Verify authenticator app is synced to correct time
- Check TOTP secret generation and storage
- Ensure QR code URL encoding is correct

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Built with ❤️ for secure, scalable authentication**