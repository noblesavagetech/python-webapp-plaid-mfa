#!/usr/bin/env python3
"""
SMTP Relay Server - Accepts emails and relays them through ProtonMail SMTP
"""
import asyncio
import logging
import os
import smtplib
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message
from email import message_from_bytes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROTON_USER = os.getenv('GMAIL_USER', '')
PROTON_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', '')

class ProtonRelayHandler(Message):
    async def handle_message(self, message):
        """Relay the email through ProtonMail"""
        try:
            recipients = message.get_all('To', [])
            logger.info(f"✓ Email received from {message.get('From')} to {recipients}")
            logger.info(f"  Subject: {message.get('Subject', '(no subject)')}")
            
            if PROTON_USER and PROTON_PASSWORD:
                await asyncio.to_thread(self.relay_via_proton, message)
                logger.info(f"✓ Email relayed successfully via ProtonMail")
            else:
                logger.warning("No ProtonMail credentials configured")
        except Exception as e:
            logger.error(f"✗ Error relaying email: {e}", exc_info=True)

    def relay_via_proton(self, message):
        """Relay the email through ProtonMail SMTP servers"""
        try:
            logger.info(f"Connecting to ProtonMail SMTP (smtp.protonmail.com:587)...")
            server = smtplib.SMTP('smtp.protonmail.com', 587, timeout=10)
            server.starttls()
            logger.info(f"Logging in as {PROTON_USER}...")
            server.login(PROTON_USER, PROTON_PASSWORD)
            logger.info(f"Sending email...")
            server.send_message(message)
            server.quit()
            logger.info(f"✓ Successfully relayed via ProtonMail SMTP")
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"✗ ProtonMail authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"✗ Failed to relay email: {e}", exc_info=True)
            raise

if __name__ == '__main__':
    logger.info("Starting SMTP Relay Server on port 25...")
    if PROTON_USER and PROTON_PASSWORD:
        logger.info(f"Relaying emails through ProtonMail ({PROTON_USER})")
    else:
        logger.warning("No ProtonMail credentials - emails will be logged but not sent")
    
    handler = ProtonRelayHandler()
    controller = Controller(handler, hostname='0.0.0.0', port=25)
    controller.start()
    logger.info("SMTP server running. Press Ctrl+C to stop.")
    
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        controller.stop()
