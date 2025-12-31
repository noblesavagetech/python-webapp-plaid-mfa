#!/usr/bin/env python3
"""
Test Vonage Verify API SMS functionality.
"""
import os
import sys
from dotenv import load_dotenv
from vonage import Auth, Vonage
from vonage_verify_legacy import VerifyRequest

# Load environment variables
load_dotenv()

def test_vonage_sms(phone_number):
    """
    Send a test SMS using Vonage Verify API.
    
    Args:
        phone_number (str): Phone number in E.164 format (e.g., +15612134181)
    """
    # Configure Vonage client
    api_key = os.getenv('VONAGE_API_KEY')
    api_secret = os.getenv('VONAGE_API_SECRET')
    brand_name = os.getenv('VONAGE_BRAND_NAME', 'BBA Services')
    
    auth = Auth(api_key=api_key, api_secret=api_secret)
    client = Vonage(auth=auth)
    
    try:
        # Start verification
        print(f"🚀 Initiating verification for {phone_number}...")
        
        # Remove + from phone number if present (Vonage expects digits only)
        phone_digits = phone_number.lstrip('+')
        
        verify_request = VerifyRequest(
            number=phone_digits,
            brand=brand_name,
            code_length=6,
            workflow_id=1  # SMS only
        )
        
        response = client.verify_legacy.start_verification(verify_request)
        
        if response.status == '0':  # Success
            request_id = response.request_id
            print("✅ SMS verification initiated successfully!")
            print(f"   Request ID: {request_id}")
            print(f"   Phone: {phone_number}")
            print(f"   Brand: {brand_name}")
            print("\n📱 A 6-digit code has been sent to the phone number.")
            print("   Check your messages and enter the code below to verify.\n")
            
            # Prompt for code verification
            code = input("🔑 Enter the 6-digit code you received: ").strip()
            
            if code:
                print(f"\n🔍 Verifying code {code}...")
                verify_response = client.verify_legacy.check(request_id, code=code)
                
                if verify_response.status == '0':
                    print("✅ Code verified successfully! SMS is working! 🎉")
                    return True
                else:
                    error_text = verify_response.error_text if hasattr(verify_response, 'error_text') else 'Unknown error'
                    print(f"❌ Verification failed: {error_text}")
                    return False
            else:
                print("⚠️  No code entered. Skipping verification.")
                return None
        else:
            error_text = response.error_text if hasattr(response, 'error_text') else 'Unknown error'
            status = response.status
            print(f"❌ Failed to send SMS")
            print(f"   Status: {status}")
            print(f"   Error: {error_text}")
            return False
        
    except Exception as e:
        print("❌ Unexpected error")
        print(f"   Error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("BBA Services - SMS Test (Vonage Verify API)")
    print("=" * 60)
    
    # Check if credentials are loaded
    api_key = os.getenv('VONAGE_API_KEY')
    api_secret = os.getenv('VONAGE_API_SECRET')
    brand_name = os.getenv('VONAGE_BRAND_NAME', 'BBA Services')
    
    if not api_key:
        print("❌ VONAGE_API_KEY not found in environment")
        return False
    
    if not api_secret:
        print("❌ VONAGE_API_SECRET not found in environment")
        return False
    
    print(f"\n📧 Configuration:")
    print(f"   Brand: {brand_name}")
    print(f"   API Key: {api_key}")
    print(f"   API Secret: {api_secret[:4]}...{api_secret[-4:]}")
    
    # Get phone number
    phone = input("\n📱 Enter phone number (with country code, e.g., +15612134181): ").strip()
    
    # Add + if not present
    if not phone.startswith('+'):
        phone = '+' + phone
    
    if len(phone) < 10:
        print("❌ Invalid phone number")
        return False
    
    result = test_vonage_sms(phone)
    print("\n" + "=" * 60)
    return result

if __name__ == "__main__":
    main()
