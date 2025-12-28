"""
Simple SMS utility using Twilio.
"""
from twilio.rest import Client
from flask import current_app
import random


def send_sms_code(phone_number, code):
    """Send SMS verification code using Twilio."""
    try:
        client = Client(
            current_app.config['TWILIO_ACCOUNT_SID'],
            current_app.config['TWILIO_AUTH_TOKEN']
        )
        
        message = client.messages.create(
            body=f"Your BBA Services verification code is: {code}",
            from_=current_app.config['TWILIO_PHONE_NUMBER'],
            to=phone_number
        )
        
        print(f"SMS sent to {phone_number}: {message.sid}")
        return True
        
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")
        return False


def generate_code():
    """Generate a 6-digit verification code."""
    return str(random.randint(100000, 999999))