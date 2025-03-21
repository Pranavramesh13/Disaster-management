import logging
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSHandler:
    def __init__(self):
        self.base_url = "https://api.globfone.com/send"  # Example URL, replace with actual Globfone API endpoint
        logger.info("Initialized SMS Handler with Globfone integration")

    def send_alert(self, to_number, message, alert_id=None):
        """Send SMS alert using Globfone"""
        try:
            logger.info(f"Sending alert to {to_number}")

            # Add alert ID to message if provided
            if alert_id:
                message = f"{message}\nAlert ID: {alert_id}"

            # Log the SMS sending attempt
            logger.info(f"Sending SMS to {to_number} with message: {message}")

            # For now, just log the message since we don't have actual Globfone API access
            # In production, this would make an API call to Globfone
            logger.info("SMS would be sent through Globfone (simulation)")
            logger.info(f"To: {to_number}")
            logger.info(f"Message: {message}")

            # Return a mock message ID
            message_id = f"GLOB_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            logger.info(f"Mock message ID generated: {message_id}")

            return message_id

        except Exception as e:
            logger.error(f"Error sending SMS to {to_number}: {str(e)}")
            return None

    def process_response(self, from_number, message_body):
        """Process incoming SMS response"""
        try:
            logger.info(f"Processing response from {from_number}: {message_body}")

            # Extract alert ID from message body if present
            alert_id = None
            message_lines = message_body.strip().split('\n')
            for line in message_lines:
                if line.startswith('Alert ID:'):
                    alert_id = line.split(':')[1].strip()
                    break

            # Check if message indicates safety confirmation
            is_safe = message_body.strip().upper() == 'YES'

            if is_safe and alert_id:
                logger.info(f"Safety confirmation received for alert {alert_id} from {from_number}")
                return {
                    'success': True,
                    'alert_id': alert_id,
                    'phone_number': from_number,
                    'is_safe': True
                }

            return {
                'success': False,
                'error': 'Invalid response format'
            }

        except Exception as e:
            logger.error(f"Error processing SMS response: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }