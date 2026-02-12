from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_agent_message(to_number, message_content):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        from_number = settings.TWILIO_PHONE_NUMBER
    except AttributeError:
        logger.error("Twilio settings not found in settings.py")
        return False

    clean_phone = str(to_number).replace(" ", "").replace("-", "")
    if len(clean_phone) == 10 and not clean_phone.startswith('+'):
        clean_phone = f"+91{clean_phone}" 
    elif not clean_phone.startswith('+'):
        clean_phone = f"+{clean_phone}"

    try:
        message = client.messages.create(
            body=message_content,      
            from_=f"whatsapp:{from_number}",
            to=f"whatsapp:{clean_phone}"
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp chat reply: {e}")
        return False