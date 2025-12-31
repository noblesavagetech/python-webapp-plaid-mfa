"""
SMS utility using Vonage Verify API for 2FA.
Purpose-built for transactional authentication codes with automatic fallback.
"""
from vonage import Auth, Vonage
from vonage_verify_legacy import VerifyRequest
from flask import current_app
import random


def send_sms_code(phone_number, code):
    """Send SMS verification code using Vonage Verify API.
    
    Args:
        phone_number: E.164 format phone number (e.g., +14155551234)
        code: 6-digit verification code (managed by Vonage)
    
    Returns:
        request_id: Vonage request ID for verification, or None if failed
    """
    try:
        # Initialize Vonage client
        api_key = current_app.config.get('VONAGE_API_KEY')
        api_secret = current_app.config.get('VONAGE_API_SECRET')
        brand_name = current_app.config.get('VONAGE_BRAND_NAME', 'BBA Services')
        
        if not api_key or not api_secret:
            print("ERROR - Missing Vonage credentials in config")
            return None
        
        auth = Auth(
            api_key=api_key,
            api_secret=api_secret
        )
        client = Vonage(auth=auth)
        
        # Start verification request
        # Vonage manages the OTP code generation and delivery
        # Remove + from phone number if present (Vonage expects digits only)
        phone_digits = phone_number.lstrip('+')
        
        verify_request = VerifyRequest(
            number=phone_digits,
            brand=brand_name,
            code_length=6,
            workflow_id=1  # SMS only (1=SMS, 6=SMS->TTS, 7=SMS->TTS->TTS)
        )
        
        response = client.verify_legacy.start_verification(verify_request)
        
        if response.status == '0':  # Success
            request_id = response.request_id
            print(f"Verification SMS sent to {phone_number}: request_id={request_id}")
            return request_id
        else:
            error = response.error_text if hasattr(response, 'error_text') else 'Unknown error'
            print(f"Failed to send SMS: {error}")
            return None
        
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")
        return None


def verify_sms_code(request_id, code):
    """Verify SMS code using Vonage Verify API.
    
    Args:
        request_id: Vonage request ID from send_sms_code()
        code: 6-digit code entered by user
    
    Returns:
        bool: True if code is valid, False otherwise
    """
    try:
        auth = Auth(
            api_key=current_app.config['VONAGE_API_KEY'],
            api_secret=current_app.config['VONAGE_API_SECRET']
        )
        client = Vonage(auth=auth)
        
        response = client.verify_legacy.check_code(request_id, code=code)
        
        if response.status == '0':  # Success
            print(f"Verification successful for request_id={request_id}")
            return True
        else:
            error = response.error_text if hasattr(response, 'error_text') else 'Invalid code'
            print(f"Verification failed: {error}")
            return False
            
    except Exception as e:
        print(f"Failed to verify code: {str(e)}")
        return False


def generate_code():
    """Generate a 6-digit verification code.
    
    Note: When using Vonage Verify API, code generation is handled by Vonage.
    This function is kept for backwards compatibility with email verification.
    """
    return str(random.randint(100000, 999999))