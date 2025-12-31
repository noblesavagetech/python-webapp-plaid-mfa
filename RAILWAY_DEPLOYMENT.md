# Railway Deployment Fix

## What Was Wrong
The app was timing out during startup because:
1. **Database migrations ran inside the app startup** - blocking the app from binding to the port
2. Railway expects apps to bind to `$PORT` within 15 seconds
3. No proper health check endpoint

## What Was Fixed
1. ✅ Removed automatic migration from `app/__init__.py`
2. ✅ Added migration to Railway's `startCommand` in `railway.json`
3. ✅ Added `/health` endpoint for health checks
4. ✅ Updated health check configuration

## Required Environment Variables in Railway
Make sure these are set in your Railway project settings:

### Required
- `DATABASE_URL` - Automatically set by Railway when you add PostgreSQL
- `SECRET_KEY` - Your Flask secret key (generate with `python -c 'import secrets; print(secrets.token_hex(32))'`)

### Email (Brevo)
- `BREVO_API_KEY` - Your Brevo API key
- `SENDER_EMAIL` - Your verified sender email
- `SENDER_NAME` - Your sender name (optional, defaults to "BBA Services")

### SMS (Vonage)
- `VONAGE_API_KEY` - Your Vonage API key
- `VONAGE_API_SECRET` - Your Vonage API secret
- `VONAGE_BRAND_NAME` - Your brand name (optional, defaults to "BBA Services")

### Optional
- `FLASK_ENV` - Set to `production` for production

## Deploy Steps
1. **Commit and push these changes:**
   ```bash
   git add .
   git commit -m "Fix Railway deployment - remove blocking migrations"
   git push origin main
   ```

2. **Verify Railway environment variables** (in Railway dashboard)
   - Go to your project → Variables tab
   - Ensure all required variables are set

3. **Monitor the deployment:**
   - Watch the build logs in Railway
   - The migration will run: `flask db upgrade`
   - Then gunicorn will start
   - Health check at `/health` should return `{"status": "ok"}`

4. **If still failing, check logs for:**
   - Database connection errors
   - Missing environment variables
   - Migration errors

## Test Locally First
```bash
# Set environment variables in .env file
export DATABASE_URL="postgresql://..."
export SECRET_KEY="your-secret-key"

# Run migration
flask db upgrade

# Start app
gunicorn --bind 0.0.0.0:8000 app:app

# Test health check
curl http://localhost:8000/health
```

## Troubleshooting
- **Still getting 502?** Check Railway logs for specific error messages
- **Migration failing?** Ensure DATABASE_URL is set correctly
- **App starting but 502?** Verify gunicorn is binding to `$PORT` environment variable
