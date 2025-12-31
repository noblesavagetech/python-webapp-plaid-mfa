"""
Amazon Pinpoint messaging service utility.
Provides SMS, email, push notifications, and analytics capabilities.
"""
import boto3
from flask import current_app
import random
import uuid
from datetime import datetime
import logging


class PinpointService:
    """Amazon Pinpoint service for multi-channel messaging."""
    
    def __init__(self):
        """Initialize Pinpoint client."""
        self.client = None
        self.application_id = None
        
    def _get_client(self):
        """Get or create Pinpoint client."""
        if self.client is None:
            self.client = boto3.client(
                'pinpoint',
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
                region_name=current_app.config['AWS_REGION']
            )
            self.application_id = current_app.config['PINPOINT_APPLICATION_ID']
        return self.client
        
    def send_sms(self, phone_number, message, message_type='TRANSACTIONAL', origination_number=None):
        """
        Send SMS via Pinpoint.
        
        Args:
            phone_number (str): Recipient phone number in E.164 format
            message (str): Message content
            message_type (str): PROMOTIONAL or TRANSACTIONAL
            origination_number (str): Optional sender phone number
            
        Returns:
            dict: Response containing message ID and delivery status
        """
        try:
            client = self._get_client()
            
            message_request = {
                'Addresses': {
                    phone_number: {
                        'ChannelType': 'SMS'
                    }
                },
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': message,
                        'MessageType': message_type
                    }
                }
            }
            
            # Add origination number if provided
            if origination_number:
                message_request['MessageConfiguration']['SMSMessage']['OriginationNumber'] = origination_number
                
            response = client.send_messages(
                ApplicationId=self.application_id,
                MessageRequest=message_request
            )
            
            result = response['MessageResponse']['Result'][phone_number]
            
            if result['StatusCode'] == 200:
                logging.info(f"SMS sent successfully to {phone_number}: {result['MessageId']}")
                return {
                    'success': True,
                    'message_id': result['MessageId'],
                    'delivery_status': result['DeliveryStatus']
                }
            else:
                logging.error(f"SMS failed to {phone_number}: {result['StatusMessage']}")
                return {
                    'success': False,
                    'error': result['StatusMessage']
                }
                
        except Exception as e:
            logging.error(f"Pinpoint SMS error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_email(self, recipient_email, subject, html_content, text_content=None, sender_email=None):
        """
        Send email via Pinpoint.
        
        Args:
            recipient_email (str): Recipient email address
            subject (str): Email subject
            html_content (str): HTML email content
            text_content (str): Optional plain text content
            sender_email (str): Optional sender email (must be verified in Pinpoint)
            
        Returns:
            dict: Response containing message ID and delivery status
        """
        try:
            client = self._get_client()
            
            email_message = {
                'Body': html_content,
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                }
            }
            
            if text_content:
                email_message['Body'] = {
                    'Html': {
                        'Data': html_content,
                        'Charset': 'UTF-8'
                    },
                    'Text': {
                        'Data': text_content,
                        'Charset': 'UTF-8'
                    }
                }
            else:
                email_message['Body'] = {
                    'Html': {
                        'Data': html_content,
                        'Charset': 'UTF-8'
                    }
                }
            
            message_request = {
                'Addresses': {
                    recipient_email: {
                        'ChannelType': 'EMAIL'
                    }
                },
                'MessageConfiguration': {
                    'EmailMessage': email_message
                }
            }
            
            # Add sender email if provided
            if sender_email:
                message_request['MessageConfiguration']['EmailMessage']['FromAddress'] = sender_email
                
            response = client.send_messages(
                ApplicationId=self.application_id,
                MessageRequest=message_request
            )
            
            result = response['MessageResponse']['Result'][recipient_email]
            
            if result['StatusCode'] == 200:
                logging.info(f"Email sent successfully to {recipient_email}: {result['MessageId']}")
                return {
                    'success': True,
                    'message_id': result['MessageId'],
                    'delivery_status': result['DeliveryStatus']
                }
            else:
                logging.error(f"Email failed to {recipient_email}: {result['StatusMessage']}")
                return {
                    'success': False,
                    'error': result['StatusMessage']
                }
                
        except Exception as e:
            logging.error(f"Pinpoint email error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_endpoint(self, user_id, channel_type, address, attributes=None):
        """
        Create or update an endpoint for targeted messaging.
        
        Args:
            user_id (str): Unique user identifier
            channel_type (str): SMS, EMAIL, PUSH, etc.
            address (str): Phone number, email address, or device token
            attributes (dict): Optional user attributes for segmentation
            
        Returns:
            dict: Endpoint creation response
        """
        try:
            client = self._get_client()
            
            endpoint_request = {
                'ChannelType': channel_type,
                'Address': address,
                'User': {
                    'UserId': user_id
                }
            }
            
            if attributes:
                endpoint_request['Attributes'] = attributes
                
            endpoint_id = str(uuid.uuid4())
            
            response = client.update_endpoint(
                ApplicationId=self.application_id,
                EndpointId=endpoint_id,
                EndpointRequest=endpoint_request
            )
            
            logging.info(f"Endpoint created for user {user_id}: {endpoint_id}")
            return {
                'success': True,
                'endpoint_id': endpoint_id,
                'response': response
            }
            
        except Exception as e:
            logging.error(f"Endpoint creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_campaign_message(self, segment_id, template_name, template_version=None):
        """
        Send a campaign message to a user segment.
        
        Args:
            segment_id (str): Target segment ID
            template_name (str): Message template name
            template_version (str): Optional template version
            
        Returns:
            dict: Campaign creation response
        """
        try:
            client = self._get_client()
            
            campaign_request = {
                'Name': f'Campaign_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'SegmentId': segment_id,
                'MessageConfiguration': {
                    'DefaultMessage': {
                        'Action': 'OPEN_APP'
                    }
                },
                'Schedule': {
                    'IsLocalTime': False,
                    'StartTime': datetime.now().isoformat(),
                    'Timezone': 'UTC'
                }
            }
            
            if template_name:
                campaign_request['TemplateConfiguration'] = {
                    'SMSTemplate': {
                        'Name': template_name,
                        'Version': template_version or '$LATEST'
                    }
                }
                
            response = client.create_campaign(
                ApplicationId=self.application_id,
                WriteCampaignRequest=campaign_request
            )
            
            campaign_id = response['CampaignResponse']['Id']
            
            # Start the campaign
            client.update_campaign(
                ApplicationId=self.application_id,
                CampaignId=campaign_id,
                WriteCampaignRequest={
                    **campaign_request,
                    'State': 'SCHEDULED'
                }
            )
            
            logging.info(f"Campaign created and started: {campaign_id}")
            return {
                'success': True,
                'campaign_id': campaign_id,
                'response': response
            }
            
        except Exception as e:
            logging.error(f"Campaign creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_analytics(self, start_date, end_date, metrics=None):
        """
        Get messaging analytics from Pinpoint.
        
        Args:
            start_date (datetime): Start date for analytics
            end_date (datetime): End date for analytics
            metrics (list): Optional list of specific metrics to retrieve
            
        Returns:
            dict: Analytics data
        """
        try:
            client = self._get_client()
            
            default_metrics = [
                'successful-delivery-rate',
                'messages-sent',
                'messages-delivered',
                'bounce-rate',
                'complaint-rate'
            ]
            
            response = client.get_application_date_range_kpi(
                ApplicationId=self.application_id,
                KpiName='successful-delivery-rate',
                StartTime=start_date,
                EndTime=end_date
            )
            
            return {
                'success': True,
                'analytics': response['ApplicationDateRangeKpiResponse']
            }
            
        except Exception as e:
            logging.error(f"Analytics retrieval error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Convenience functions for backwards compatibility
pinpoint_service = PinpointService()


def send_sms_code(phone_number, code):
    """Send SMS verification code using Pinpoint (backwards compatible)."""
    message = f"Your BBA Services verification code is: {code}"
    result = pinpoint_service.send_sms(phone_number, message, 'TRANSACTIONAL')
    return result.get('success', False)


def send_verification_email(user_email, verification_code):
    """Send email verification code using Pinpoint (backwards compatible)."""
    subject = "Verify Your Email - BBA Services"
    html_content = f"""
    <h2>Welcome to BBA Services!</h2>
    <p>Your verification code is: <strong>{verification_code}</strong></p>
    <p>Enter this code to verify your email address.</p>
    """
    
    result = pinpoint_service.send_email(user_email, subject, html_content)
    return result.get('success', False)


def generate_code():
    """Generate a 6-digit verification code."""
    return str(random.randint(100000, 999999))


def create_user_endpoint(user_id, email=None, phone=None, attributes=None):
    """Create Pinpoint endpoints for a user."""
    endpoints = []
    
    if email:
        result = pinpoint_service.create_endpoint(user_id, 'EMAIL', email, attributes)
        endpoints.append(result)
        
    if phone:
        result = pinpoint_service.create_endpoint(user_id, 'SMS', phone, attributes)
        endpoints.append(result)
        
    return endpoints