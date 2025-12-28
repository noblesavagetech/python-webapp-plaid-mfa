#!/usr/bin/env python3
"""
Simple SMTP server that accepts all emails and prints them to console
"""
import asyncio
import logging
from aiosmtpd.controller import Controller

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class EmailHandler:
    async def handle_DATA(self, server, session, envelope):
        """Handle incoming email"""
        logger.info(f"Message received from: {envelope.mail_from}")
        logger.info(f"Recipients: {envelope.rcpt_tos}")
        logger.info(f"Message content:\n{envelope.content.decode('utf8')}\n")
        return '250 Message accepted'


async def main():
    """Start the SMTP server"""
    handler = EmailHandler()
    controller = Controller(handler, hostname='0.0.0.0', port=25)
    controller.start()
    logger.info("SMTP server running on port 25")
    
    try:
        await asyncio.sleep(10 * 3600)  # Run for 10 hours
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()


if __name__ == '__main__':
    asyncio.run(main())
