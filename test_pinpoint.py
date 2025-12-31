#!/usr/bin/env python3
"""
Test script for Amazon Pinpoint integration.
Run this script to verify SMS and email functionality.
"""

import os
import sys
from datetime import datetime, timedelta

# Add app directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from flask import Flask
from app.config import Config
from app.utils.pinpoint import pinpoint_service, create_user_endpoint
from app.utils.sms import send_sms_code, generate_code
from app.utils.email import send_verification_email, send_marketing_email


def create_test_app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


def test_pinpoint_configuration():
    """Test if Pinpoint is properly configured."""
    print("🔧 Testing Pinpoint Configuration...")
    
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'PINPOINT_APPLICATION_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or environment configuration.")
        return False
    else:
        print("✅ All required environment variables are set.")
        return True


def test_sms_functionality():
    """Test SMS sending via Pinpoint."""
    print("\n📱 Testing SMS Functionality...")
    
    # Get test phone number from user
    phone = input("Enter a test phone number (E.164 format, e.g., +1234567890): ")
    if not phone.startswith('+'):
        print("❌ Please provide phone number in E.164 format (starting with +)")
        return False
    
    # Generate and send test code
    code = generate_code()
    print(f"Sending verification code: {code}")
    
    try:
        success = send_sms_code(phone, code)
        if success:
            print(f"✅ SMS sent successfully to {phone}")
            return True
        else:
            print(f"❌ Failed to send SMS to {phone}")
            return False
    except Exception as e:
        print(f"❌ SMS test failed: {str(e)}")
        return False


def test_email_functionality():
    """Test email sending via Pinpoint (with Brevo fallback)."""
    print("\n📧 Testing Email Functionality...")
    
    # Get test email from user
    email = input("Enter a test email address: ")
    
    # Generate and send test verification email
    code = generate_code()
    print(f"Sending verification email with code: {code}")
    
    try:
        success = send_verification_email(email, code, use_pinpoint=True)
        if success:
            print(f"✅ Verification email sent successfully to {email}")
            
            # Test marketing email if Pinpoint is configured
            if os.getenv('PINPOINT_SENDER_EMAIL'):
                print("Testing marketing email via Pinpoint...")
                result = send_marketing_email(
                    user_email=email,
                    subject="Test Marketing Email",
                    html_content="<h1>This is a test marketing email from Pinpoint!</h1><p>If you receive this, Pinpoint email is working correctly.</p>"
                )
                if result.get('success'):
                    print("✅ Marketing email sent via Pinpoint")
                else:
                    print(f"❌ Marketing email failed: {result.get('error')}")
            
            return True
        else:
            print(f"❌ Failed to send email to {email}")
            return False
    except Exception as e:
        print(f"❌ Email test failed: {str(e)}")
        return False


def test_endpoint_creation():
    """Test Pinpoint endpoint creation for user targeting."""
    print("\n👤 Testing User Endpoint Creation...")
    
    test_user_id = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    test_email = input("Enter email for endpoint test: ")
    test_phone = input("Enter phone for endpoint test (optional, press Enter to skip): ")
    
    try:
        endpoints = create_user_endpoint(
            user_id=test_user_id,
            email=test_email,
            phone=test_phone if test_phone else None,
            attributes={
                "test_user": ["true"],
                "created_date": [datetime.now().strftime('%Y-%m-%d')]
            }
        )
        
        success_count = sum(1 for ep in endpoints if ep.get('success'))
        print(f"✅ Created {success_count}/{len(endpoints)} endpoints for user {test_user_id}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Endpoint creation failed: {str(e)}")
        return False


def test_analytics():
    """Test Pinpoint analytics retrieval."""
    print("\n📊 Testing Analytics Retrieval...")
    
    try:
        # Get analytics for the last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        analytics = pinpoint_service.get_analytics(start_date, end_date)
        
        if analytics.get('success'):
            print("✅ Analytics retrieved successfully")
            print("Analytics data structure:")
            print(analytics['analytics'].keys() if isinstance(analytics['analytics'], dict) else "Raw analytics data available")
            return True
        else:
            print(f"❌ Analytics retrieval failed: {analytics.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Analytics test failed: {str(e)}")
        return False


def main():
    """Run all Pinpoint tests."""
    print("🚀 Amazon Pinpoint Integration Test Suite")
    print("=" * 50)
    
    # Create Flask app context for configuration
    app = create_test_app()
    
    with app.app_context():
        tests = [
            ("Configuration", test_pinpoint_configuration),
            ("SMS Functionality", test_sms_functionality),
            ("Email Functionality", test_email_functionality),
            ("User Endpoints", test_endpoint_creation),
            ("Analytics", test_analytics)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except KeyboardInterrupt:
                print(f"\n⏹️ Test interrupted by user")
                break
            except Exception as e:
                print(f"❌ {test_name} test encountered an error: {str(e)}")
                results[test_name] = False
        
        # Print summary
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        passed_count = sum(results.values())
        total_count = len(results)
        
        print(f"\nOverall: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("\n🎉 All tests passed! Pinpoint is ready for production.")
        else:
            print(f"\n⚠️ {total_count - passed_count} tests failed. Check your configuration.")


if __name__ == "__main__":
    main()