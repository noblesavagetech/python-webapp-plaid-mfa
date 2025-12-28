"""
Email sending utility using Brevo HTTP API (not SMTP).
Railway blocks SMTP ports, so we use the HTTP API instead.
"""
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from flask import current_app


def send_verification_email(user_email, verification_code):
    """
    Send 6-digit verification code via Brevo HTTP API.
    
    Args:
        user_email: The recipient's email address
        verification_code: The 6-digit verification code
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Configure Brevo API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = current_app.config['BREVO_API_KEY']
        
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # Create email content
        sender = {
            "name": current_app.config['SENDER_NAME'],
            "email": current_app.config['SENDER_EMAIL']
        }
        
        to = [{"email": user_email}]
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 40px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 30px; }}
                .code {{ 
                    display: inline-block; 
                    padding: 20px 40px; 
                    background: #f8f9fa;
                    color: #667eea; 
                    font-size: 36px;
                    font-weight: bold;
                    border-radius: 6px;
                    letter-spacing: 8px;
                    margin: 20px 0;
                }}
                .footer {{ 
                    background: #f8f9fa; 
                    padding: 30px; 
                    text-align: center; 
                    font-size: 13px; 
                    color: #666; 
                    border-top: 1px solid #eee;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 BBA Services</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Email Verification</p>
                </div>
                <div class="content">
                    <h2 style="color: #333; margin-bottom: 20px;">Verify Your Email</h2>
                    <p style="margin-bottom: 20px;">Thank you for creating an account. Please use the verification code below to confirm your email address:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <div class="code">{verification_code}</div>
                    </div>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        <strong>Security Note:</strong> This code will expire in 24 hours. If you didn't create an account, please ignore this email.
                    </p>
                </div>
                <div class="footer">
                    <p style="margin: 0 0 10px 0;"><strong>BBA Services</strong></p>
                    <p style="margin: 0;">This is an automated message from {current_app.config['SENDER_EMAIL']}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = "Verify Your Email - BBA Services"
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            html_content=html_content,
            sender=sender,
            subject=subject
        )
        
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"Verification email sent successfully to {user_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email to {user_email}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def send_mfa_setup_email(user_email, totp_secret):
    """
    Send TOTP setup instructions via Brevo HTTP API.
    
    Args:
        user_email: The recipient's email address
        totp_secret: The TOTP secret key
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Configure Brevo API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = current_app.config['BREVO_API_KEY']
        
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # Create email content
        sender = {
            "name": current_app.config['SENDER_NAME'],
            "email": current_app.config['SENDER_EMAIL']
        }
        
        to = [{"email": user_email}]
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 40px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 30px; }}
                .secret {{ 
                    display: inline-block; 
                    padding: 15px 25px; 
                    background: #f8f9fa;
                    color: #667eea; 
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 6px;
                    letter-spacing: 2px;
                    margin: 20px 0;
                    font-family: monospace;
                }}
                .footer {{ 
                    background: #f8f9fa; 
                    padding: 30px; 
                    text-align: center; 
                    font-size: 13px; 
                    color: #666; 
                    border-top: 1px solid #eee;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 BBA Services</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Two-Factor Authentication Setup</p>
                </div>
                <div class="content">
                    <h2 style="color: #333; margin-bottom: 20px;">Set Up MFA</h2>
                    <p style="margin-bottom: 20px;">Your email has been verified! For security, we use two-factor authentication (MFA).</p>
                    
                    <p><strong>Your TOTP Secret:</strong></p>
                    <div style="text-align: center;">
                        <div class="secret">{totp_secret}</div>
                    </div>
                    
                    <p style="margin-top: 30px;"><strong>Setup Instructions:</strong></p>
                    <ol style="margin-left: 20px; color: #555; line-height: 1.8;">
                        <li>Download an authenticator app (Google Authenticator, Authy, 1Password, etc.)</li>
                        <li>Open the app and select "Add Account" or "Scan QR Code"</li>
                        <li>Enter the secret above manually or scan the QR code on the setup page</li>
                        <li>Use the generated 6-digit codes to complete setup</li>
                    </ol>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        <strong>Security Note:</strong> Keep this secret safe. Anyone with access to it can generate valid codes for your account.
                    </p>
                </div>
                <div class="footer">
                    <p style="margin: 0 0 10px 0;"><strong>BBA Services</strong></p>
                    <p style="margin: 0;">This is an automated message from {current_app.config['SENDER_EMAIL']}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = "Set Up Two-Factor Authentication - BBA Services"
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            html_content=html_content,
            sender=sender,
            subject=subject
        )
        
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"MFA setup email sent successfully to {user_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send MFA email to {user_email}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False