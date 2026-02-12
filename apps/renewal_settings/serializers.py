from rest_framework import serializers
from .models import RenewalSettings
from apps.call_provider.models import CallProviderConfig
from apps.call_provider.serializers import CallProviderConfigSerializer

PROVIDER_CAPABILITIES = {
    'twilio': {'recording': True, 'analytics': True, 'max_limit': 100, 'max_duration': 240},
    'exotel': {'recording': True, 'analytics': True, 'max_limit': 50,  'max_duration': 60},
    'ubona':  {'recording': False, 'analytics': False, 'max_limit': 20, 'max_duration': 30},
    'custom': {'recording': True, 'analytics': True, 'max_limit': 100, 'max_duration': 120}
}

class RenewalSettingsSerializer(serializers.ModelSerializer):
    active_provider_details = CallProviderConfigSerializer(source='active_provider', read_only=True)
    
    twilio_account_sid = serializers.CharField(required=False, allow_blank=True, write_only=True)
    twilio_auth_token = serializers.CharField(required=False, allow_blank=True, write_only=True)
    twilio_from_number = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    exotel_api_key = serializers.CharField(required=False, allow_blank=True, write_only=True)
    exotel_api_token = serializers.CharField(required=False, allow_blank=True, write_only=True)
    exotel_subdomain = serializers.CharField(required=False, allow_blank=True, write_only=True)
    exotel_account_sid = serializers.CharField(required=False, allow_blank=True, write_only=True)
    exotel_caller_id = serializers.CharField(required=False, allow_blank=True, write_only=True)

    ubona_api_key = serializers.CharField(required=False, allow_blank=True, write_only=True)
    ubona_api_url = serializers.CharField(required=False, allow_blank=True, write_only=True)
    ubona_account_sid = serializers.CharField(required=False, allow_blank=True, write_only=True)
    ubona_caller_id = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = RenewalSettings
        fields = [
            'id',
            'auto_refresh_enabled',
            'show_edit_case_button',
            'enforce_provider_limits',
            
            'default_renewal_period',
            'auto_assign_cases',
            
            'enable_call_integration',
            
            'is_call_integration_testing',
            'is_sms_integration_testing',
            'is_whatsapp_integration_testing',
            
            'default_call_duration',
            'max_concurrent_calls',
            'enable_call_recording',
            'enable_call_analytics',
            
            'active_provider', 
            'active_provider_details',
            
            'twilio_account_sid', 'twilio_auth_token', 'twilio_from_number',
            'exotel_api_key', 'exotel_api_token', 'exotel_subdomain', 'exotel_account_sid', 'exotel_caller_id',
            'ubona_api_key', 'ubona_api_url', 'ubona_account_sid', 'ubona_caller_id',
        ]
        read_only_fields = [
            'active_provider', 
            'id', 
            'is_call_integration_testing', 
            'is_sms_integration_testing', 
            'is_whatsapp_integration_testing'
        ]

    def validate(self, data):
        current_type = None
        if self.instance and self.instance.active_provider:
            current_type = self.instance.active_provider.provider_type
        
        if not current_type:
            return data

        rules = PROVIDER_CAPABILITIES.get(current_type, {})
        
        if data.get('enable_call_recording') and not rules.get('recording'):
             raise serializers.ValidationError({
                 "enable_call_recording": f"{current_type.capitalize()} does not support Call Recording."
             })

        if data.get('enable_call_analytics') and not rules.get('analytics'):
             raise serializers.ValidationError({
                 "enable_call_analytics": f"{current_type.capitalize()} does not support Call Analytics."
             })
             
        req_duration = data.get('default_call_duration')
        allow_duration = rules.get('max_duration', 0)
        
        if req_duration and allow_duration > 0 and req_duration > allow_duration:
            raise serializers.ValidationError({
                "default_call_duration": f"{current_type.capitalize()} allows max duration of {allow_duration} minutes."
            })

        req_limit = data.get('max_concurrent_calls')
        allow_limit = rules.get('max_limit', 0)
        
        if req_limit and allow_limit > 0 and req_limit > allow_limit:
            raise serializers.ValidationError({
                "max_concurrent_calls": f"{current_type.capitalize()} allows max {allow_limit} concurrent calls."
            })

        return data


class QuickMessageSettingsSerializer(serializers.ModelSerializer):
    from apps.sms_provider.models import SmsProvider
    from apps.whatsapp_provider.models import WhatsAppProvider
    wa_access_token = serializers.CharField(required=False, allow_blank=True, write_only=True)
    wa_phone_number_id = serializers.CharField(required=False, allow_blank=True, write_only=True)
    wa_business_account_id = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    sms_api_key = serializers.CharField(required=False, allow_blank=True, write_only=True) 
    sms_auth_token = serializers.CharField(required=False, allow_blank=True, write_only=True)
    sms_sender_id = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        from .models import QuickMessageSettings
        model = QuickMessageSettings
        fields = [
            'id',
            'enable_quick_message_integration',
            'active_sms_provider',
            'active_whatsapp_provider',
            
            'enable_delivery_reports',
            'enable_message_analytics',
            'rate_limit_per_minute',
            'daily_message_limit',
            
            'policy_renewal_reminder_template',
            'claim_status_update_template',
            'payment_confirmation_template',
            
            'wa_access_token', 'wa_phone_number_id', 'wa_business_account_id',
            'sms_api_key', 'sms_auth_token', 'sms_sender_id'
        ]