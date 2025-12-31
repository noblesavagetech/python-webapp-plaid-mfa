"""
Email sending utility using Brevo (SendinBlue) for transactional emails.
"""
import sib_api_v3_sdk
from flask import current_app


def send_verification_email(user_email, verification_code):
    """
    Send email verification code using Brevo.
    
    Args:
        user_email (str): Recipient email address
        verification_code (str): Verification code
        
    Returns:
        bool: Success status
    """
    subject = "Verify Your Email - BBA Services"
    html_content = f"""
    <h2>Welcome to BBA Services!</h2>
    <p>Your verification code is: <strong>{verification_code}</strong></p>
    <p>Enter this code to verify your email address.</p>
    """
    
    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = current_app.config['BREVO_API_KEY']
        
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        sender = {
            "name": current_app.config['SENDER_NAME'],
            "email": current_app.config['SENDER_EMAIL']
        }
        
        to = [{"email": user_email}]
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            html_content=html_content,
            sender=sender,
            subject=subject
        )
        
        api_instance.send_transac_email(send_smtp_email)
        print(f"Email sent via Brevo to {user_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email via Brevo: {str(e)}")
        return False