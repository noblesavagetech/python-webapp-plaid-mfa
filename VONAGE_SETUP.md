# Vonage Setup Guide for BBA Services 2FA

## Quick Setup (5 minutes)

### 1. Create Vonage Account
1. Go to https://dashboard.nexmo.com/sign-up
2. Create free account (includes $2 credit for testing)
3. Verify your email

### 2. Get API Credentials
1. Login to https://dashboard.nexmo.com/
2. Find "API Key" and "API Secret" on the dashboard
3. Copy both values

### 3. Configure Environment Variables

**Local Development (.env file):**
```bash
# Vonage Credentials
VONAGE_API_KEY=your_api_key_here
VONAGE_API_SECRET=your_api_secret_here
VONAGE_BRAND_NAME=BBA Services

# Brevo (existing)
BREVO_API_KEY=your_brevo_key
SENDER_EMAIL=noreply@bbaservices.com
SENDER_NAME=BBA Services

# Database
DATABASE_URL=sqlite:///dev.db
SECRET_KEY=dev-secret-key
```

**Railway Production:**
```bash
railway variables set VONAGE_API_KEY=your_api_key_here
railway variables set VONAGE_API_SECRET=your_api_secret_here
railway variables set VONAGE_BRAND_NAME="BBA Services"

# Remove old AWS variables
railway variables unset AWS_ACCESS_KEY_ID
railway variables unset AWS_SECRET_ACCESS_KEY
railway variables unset AWS_REGION
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Database Migration
```bash
# If using local SQLite
flask db upgrade

# If using Railway PostgreSQL, wait until deployed
```

### 6. Test SMS Flow

**Test Phone Numbers (Free Testing):**
Vonage provides test numbers that don't use your credits:
- Test Number: Any number you verify in dashboard
- Test Code: Displayed in dashboard when using test mode

**Real Testing:**
```python
# 1. Register user
POST /signup
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

# 2. Enable MFA
POST /enable-mfa
{
  "phone": "+14155551234"  # Must be E.164 format
}
# → SMS sent with code

# 3. Verify and enable
POST /enable-mfa
{
  "phone": "+14155551234",
  "sms_code": "123456"
}
# → MFA enabled

# 4. Login
POST /login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
# → Redirects to SMS verification

# 5. Request SMS code
GET /request-sms-code
# → SMS sent

# 6. Complete login
POST /login
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "sms_code": "123456"
}
# → Login successful
```

## Phone Number Format

**Always use E.164 format:**
- ✅ Correct: `+14155551234` (country code + number)
- ❌ Wrong: `4155551234` (missing +1)
- ❌ Wrong: `(415) 555-1234` (has formatting)

**Country Codes:**
- USA/Canada: `+1`
- UK: `+44`
- Australia: `+61`

## Pricing

**Vonage Verify API Pricing (as of 2025):**
- US/Canada: ~$0.05 per verification
- UK: ~$0.04 per verification
- India: ~$0.03 per verification
- Most countries: $0.03-$0.06 per verification

**Free Credits:**
- New accounts get $2 credit (~40-60 verifications)
- Perfect for development and testing

## SMS Message Example

Users will receive:
```
BBA Services verification code: 123456
```

Powered by Vonage's delivery network with automatic fallback to voice if SMS fails.

## Troubleshooting

### "Invalid Credentials"
- Check VONAGE_API_KEY and VONAGE_API_SECRET are correct
- Ensure no extra spaces in environment variables
- Verify account is active (not suspended)

### "Number not in E.164 format"
- Add country code: `+1` for US/Canada
- Remove all formatting (spaces, dashes, parentheses)
- Example: `(415) 555-1234` → `+14155551234`

### "Insufficient balance"
- Add credit to Vonage account
- Or use test numbers from dashboard

### SMS not received
- Check number is valid and can receive SMS
- Verify no typos in phone number
- Check Vonage dashboard for delivery status
- Voice fallback will be attempted automatically

## Security Best Practices

✅ **Store credentials securely** - Use environment variables, never commit to git
✅ **Rate limit requests** - Prevent abuse (e.g., 5 SMS per hour per user)
✅ **Validate phone numbers** - Check format before sending
✅ **Clear request IDs** - After verification completes
✅ **Monitor usage** - Set up billing alerts in Vonage dashboard
✅ **Use HTTPS only** - Never send codes over plain HTTP

## Compliance

**This implementation complies with:**
- TCPA (US) - Transactional SMS only
- GDPR (EU) - User consent during onboarding
- CAN-SPAM - No marketing messages
- CTIA Guidelines - Security notifications only

**Required disclosures:**
- Phone numbers collected for security purposes
- SMS used only for account authentication
- Users can disable MFA anytime

## Support

**Vonage Documentation:**
- Verify API: https://developer.vonage.com/en/verify/overview
- Python SDK: https://github.com/Vonage/vonage-python-sdk
- Code Examples: https://developer.vonage.com/en/verify/code-snippets

**Need Help?**
- Vonage Support: https://dashboard.nexmo.com/support
- Community Forum: https://community.vonage.com/

---

**Setup Complete!** 🎉

You're now ready to use Vonage Verify API for secure, reliable 2FA.
