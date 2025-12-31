# Amazon Pinpoint Configuration Guide 🚀

Successfully upgraded from AWS SNS to Amazon Pinpoint for enhanced multi-channel messaging capabilities!

## What Changed

### 1. Dependencies
- ✅ Updated: `boto3>=1.26.0`, `botocore>=1.29.0`
- ✅ Added: Amazon Pinpoint support via boto3

### 2. Configuration (config.py)
- ✅ Added: `PINPOINT_APPLICATION_ID` - Your Pinpoint project ID
- ✅ Added: `PINPOINT_ORIGINATION_NUMBER` - Optional dedicated SMS number
- ✅ Added: `PINPOINT_SENDER_EMAIL` - Verified sender email for Pinpoint

### 3. New Pinpoint Service (utils/pinpoint.py)
- ✅ Full Pinpoint client with SMS, Email, Push notification support
- ✅ User endpoint management for targeted messaging
- ✅ Campaign management and analytics
- ✅ Backwards compatibility with existing functions

### 4. Updated Services
- ✅ SMS Service (utils/sms.py): Now uses Pinpoint with enhanced delivery tracking
- ✅ Email Service (utils/email.py): Pinpoint primary, Brevo fallback

## Pinpoint Benefits vs SNS

| Feature | SNS | Pinpoint |
|---------|-----|----------|
| **Analytics** | ❌ Basic | ✅ Comprehensive delivery metrics |
| **User Segmentation** | ❌ No | ✅ Advanced audience targeting |
| **Campaign Management** | ❌ No | ✅ Scheduled campaigns & A/B testing |
| **Multi-Channel** | ❌ SMS only | ✅ SMS, Email, Push, Voice |
| **Templates** | ❌ No | ✅ Reusable message templates |
| **Delivery Optimization** | ❌ Basic | ✅ Time-zone aware & quiet hours |
| **Cost** | Lower | Slightly higher but more features |

## AWS Pinpoint Setup Instructions

### Step 1: Create Pinpoint Project
```bash
# Log into AWS Console
# Navigate to Amazon Pinpoint
# Click "Create a project"
# Choose a project name (e.g., "bba-services-messaging")
# Note down the Application ID
```

### Step 2: Configure SMS Channel
```bash
# In Pinpoint Console → Settings → SMS and voice
# Enable SMS channel
# Request production access (if needed)
# Optional: Request dedicated origination number
```

### Step 3: Configure Email Channel
```bash
# In Pinpoint Console → Settings → Email
# Enable email channel
# Verify sender email address
# Configure sender reputation tracking
```

### Step 4: Set Up Analytics
```bash
# In Pinpoint Console → Analytics
# Enable event streaming (optional)
# Configure delivery reports
# Set up conversion tracking
```

### Step 5: Environment Variables
```bash
# Add to your .env file or Railway environment:
PINPOINT_APPLICATION_ID=your_application_id_here
PINPOINT_SENDER_EMAIL=verified@yourdomain.com
PINPOINT_ORIGINATION_NUMBER=+1234567890  # Optional dedicated number

# Existing AWS credentials (same as before):
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1  # Or your preferred region
```

## New Capabilities Unlocked

### 1. User Endpoint Management
```python
from app.utils.pinpoint import create_user_endpoint

# Register user for targeted messaging
endpoints = create_user_endpoint(
    user_id="user_123",
    email="user@example.com",
    phone="+1234567890",
    attributes={
        "plan_type": ["premium"],
        "signup_date": ["2024-01-15"],
        "location": ["US"]
    }
)
```

### 2. Marketing Campaigns
```python
from app.utils.email import send_marketing_email

# Send marketing email with analytics
result = send_marketing_email(
    user_email="user@example.com",
    subject="New Features Available!",
    html_content="<h1>Check out our latest updates...</h1>"
)
```

### 3. Advanced SMS with Delivery Tracking
```python
from app.utils.pinpoint import pinpoint_service

# Send SMS with detailed response
result = pinpoint_service.send_sms(
    phone_number="+1234567890",
    message="Your transaction is complete!",
    message_type='TRANSACTIONAL'
)

print(f"Message ID: {result['message_id']}")
print(f"Delivery Status: {result['delivery_status']}")
```

### 4. Analytics and Reporting
```python
from app.utils.pinpoint import pinpoint_service
from datetime import datetime, timedelta

# Get messaging analytics
analytics = pinpoint_service.get_analytics(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)
```

## Migration Checklist

- [ ] **AWS Setup**
  - [ ] Create Pinpoint project in AWS Console
  - [ ] Configure SMS channel (production access if needed)
  - [ ] Configure email channel with verified sender
  - [ ] Note down Application ID

- [ ] **Code Deployment**
  - [ ] Deploy updated code to production
  - [ ] Update environment variables
  - [ ] Test SMS functionality
  - [ ] Test email functionality

- [ ] **Verification**
  - [ ] Send test SMS verification code
  - [ ] Send test email verification
  - [ ] Check Pinpoint analytics dashboard
  - [ ] Verify delivery reports

- [ ] **Optimization** (Optional)
  - [ ] Set up user segments for targeted campaigns
  - [ ] Create message templates
  - [ ] Configure quiet hours and delivery optimization
  - [ ] Set up conversion tracking

## Cost Optimization Tips

1. **Use Transactional vs Promotional**: Mark verification codes as `TRANSACTIONAL` for better deliverability
2. **Dedicated Numbers**: Consider dedicated origination numbers for high-volume SMS
3. **Email Verification**: Verify your domain in SES for better email reputation
4. **Monitoring**: Set up CloudWatch alarms for cost monitoring
5. **Segmentation**: Use targeted campaigns instead of mass broadcasts

## Troubleshooting

### Common Issues:
1. **SMS Delivery Issues**: Check if production access is enabled
2. **Email Bounce**: Ensure sender email is verified in Pinpoint
3. **High Costs**: Review message types (use TRANSACTIONAL for verification codes)
4. **Analytics Missing**: Verify Application ID is correct in config

### Support Resources:
- [AWS Pinpoint Documentation](https://docs.aws.amazon.com/pinpoint/)
- [SMS Best Practices](https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-sms-best-practices.html)
- [Email Deliverability Guide](https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-email-deliverability.html)

---

**Migration Date**: December 29, 2025
**Status**: ✅ Ready for Production
**Next Steps**: Deploy and monitor delivery metrics in Pinpoint Console