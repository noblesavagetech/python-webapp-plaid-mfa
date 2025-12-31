"""
Test script for sending emails via Brevo API.
"""
import os
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Load environment variables
load_dotenv()

def test_brevo_email(recipient_email):
    """
    Send a test email using Brevo API.
    
    Args:
        recipient_email (str): Email address to send test email to
    """
    # Configure Brevo API
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    
    # Email details
    sender = {
        "name": os.getenv('SENDER_NAME', 'BBA Services'),
        "email": os.getenv('SENDER_EMAIL', 'noreply@bbaservices.org')
    }
    
    to = [{"email": recipient_email}]
    
    subject = "Test Email - BBA Services"
    html_content = """
    <html>
        <body>
            <h2>🎉 Email Test Successful!</h2>
            <p>This is a test email from BBA Services.</p>
            <p>If you're receiving this, your Brevo email configuration is working correctly.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                Sent via Brevo API on December 31, 2025
            </p>
        </body>
    </html>
    """
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        sender=sender,
        subject=subject
    )
    
    try:
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("✅ Email sent successfully!")
        print(f"   Message ID: {api_response.message_id}")
        print(f"   Recipient: {recipient_email}")
        print(f"   Sender: {sender['email']}")
        return True
        
    except ApiException as e:
        print("❌ Failed to send email")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print("❌ Unexpected error")
        print(f"   Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("BBA Services - Email Test")
    print("=" * 60)
    
    # Check if credentials are loaded
    api_key = os.getenv('BREVO_API_KEY')
    sender_email = os.getenv('SENDER_EMAIL')
    
    if not api_key:
        print("❌ BREVO_API_KEY not found in environment")
        exit(1)
    
    if not sender_email:
        print("❌ SENDER_EMAIL not found in environment")
        exit(1)
    
    print(f"\n📧 Configuration:")
    print(f"   Sender: {sender_email}")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Prompt for recipient email
    recipient = input("\n📬 Enter recipient email address: ").strip()
    
    if not recipient or '@' not in recipient:
        print("❌ Invalid email address")
        exit(1)
    
    print(f"\n🚀 Sending test email to {recipient}...")
    test_brevo_email(recipient)
    print("\n" + "=" * 60)
