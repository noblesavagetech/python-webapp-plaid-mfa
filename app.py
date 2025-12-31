"""
Flask Email Verification App with MFA
Main application entry point (for compatibility)
"""
from app import create_app

# Create app instance for gunicorn or compatibility
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)