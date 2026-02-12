import logging
from django.utils import timezone
from django.db import transaction
from django.db.models import F

from apps.renewal_settings.models import QuickMessageSettings
from apps.sms_provider.services import SmsService
from apps.whatsapp_provider.services import WhatsAppService

logger = logging.getLogger(__name__)

class limitReachedException(Exception):
    pass

class QuickMessageService:
    def send_quick_message(self, recipient_phone, template_text, context, channel='whatsapp'):
        settings = QuickMessageSettings.objects.filter(is_active_configuration=True).last()
        if not settings or not settings.enable_quick_message_integration:
            raise Exception("Quick Message Integration is not enabled in settings.")

        final_message = self._render_template(template_text, context)

        if channel == 'whatsapp':
            return self._handle_whatsapp(settings, recipient_phone, final_message, context)
        elif channel == 'sms':
            return self._handle_sms(settings, recipient_phone, final_message, context)
        else:
            raise Exception(f"Unsupported channel: {channel}")

    def _render_template(self, template_text, context):
        if not template_text:
            return ""
        
        rendered = template_text
        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered

    def _handle_whatsapp(self, settings, phone, message, context):
        provider = settings.active_whatsapp_provider
        if not provider:
            raise Exception("No active WhatsApp provider configured in Quick Message Settings.")

        self._check_limits(provider, settings)
        wa_service = WhatsAppService().get_service_instance(provider_id=provider.id)
        response = wa_service.send_text_message(
            to_phone=phone,
            text_content=message,
            customer_id=context.get('customer_id'),
            case_id=context.get('case_id')
        )
        
        return response

    def _handle_sms(self, settings, phone, message, context):
        provider = settings.active_sms_provider
        if not provider:
            raise Exception("No active SMS provider configured in Quick Message Settings.")

        self._check_limits(provider, settings)

        sms_service = SmsService().get_service_instance(provider_id=provider.id)
        
        response = sms_service.send_sms(
            to_phone=phone,
            message=message,
            check_notifications=True,
            customer=context.get('customer_id')
        )
        
        return response

    def _check_limits(self, provider, settings):
        limit_daily = settings.daily_message_limit
        
        if provider.messages_sent_today >= limit_daily:
            raise limitReachedException(f"Daily message limit ({limit_daily}) reached for this provider.")
