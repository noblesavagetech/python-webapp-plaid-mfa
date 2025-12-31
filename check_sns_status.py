#!/usr/bin/env python3
"""
Check AWS SNS account status (sandbox vs production)
"""
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

def check_sns_status():
    """Check if SNS account is in sandbox mode."""
    try:
        sns = boto3.client(
            'sns',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        # Try to get SMS attributes
        response = sns.get_sms_attributes()
        print("SMS Attributes:", response.get('attributes', {}))
        
        # Check for spend limit (sandbox accounts have very low limits)
        spend_limit = response['attributes'].get('MonthlySpendLimit', 'Unknown')
        print(f"Monthly Spend Limit: ${spend_limit}")
        
        if spend_limit == '1.00':
            print("🟡 You're likely in SANDBOX mode (spend limit = $1)")
            print("   - You can only send to verified phone numbers")
            print("   - Go to SNS console to add verified numbers")
        else:
            print("✅ You appear to be in PRODUCTION mode")
            
    except Exception as e:
        print(f"Error checking SNS status: {e}")

if __name__ == "__main__":
    check_sns_status()