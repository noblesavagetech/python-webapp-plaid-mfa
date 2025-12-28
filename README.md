# Python-Webapp (Financial Health)

This repository contains a Flask-based web application for financial health assessment. It includes JWT-based authentication, a questionnaire API, and integration stubs for Wave Apps OAuth.

Quick start (development using Docker Compose):

1. Copy environment variables:

```bash
cp .env.example .env
# edit .env and set values
```

2. Build and run with Docker Compose:

```bash
docker compose up --build
```

3. The API will be available at http://localhost:5000

Useful endpoints:
- `POST /api/auth/register` — register with `email` and `password`
- `POST /api/auth/login` — login and receive JWT
- `POST /api/questionnaire` — submit questionnaire (authenticated)
- `GET /api/questionnaire` — list user's questionnaire responses (authenticated)
- `GET /api/wave/connect` — start Wave OAuth flow (authenticated)

Notes:
- Run database migrations with Flask-Migrate after first run.
- Wave OAuth handlers are provided as a stub and need to be completed with secure state handling and token persistence.
# python-webapp-plaid-mfa