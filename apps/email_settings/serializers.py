from ngrok import default
from rest_framework import serializers
from .models import EmailAccount, EmailModuleSettings, ClassificationRule

class EmailAccountSerializer(serializers.ModelSerializer):
    access_credential = serializers.CharField(write_only=True,required=False)
    specific_provider_name = serializers.CharField(source='specific_provider.name', read_only=True,default=None)
    class Meta:
        model = EmailAccount
        fields = [
            'id', 'account_name', 'email_address', 'email_provider',
            'imap_server', 'imap_port', 'smtp_server', 'smtp_port',
            'use_ssl_tls', 'auto_sync_enabled', 'sync_interval_minutes',
            'access_credential', 'sending_method', 'specific_provider',      
            'specific_provider_name', 'is_default_sender',
            'connection_status', 'last_sync_at', 'last_sync_log',
            'created_at', 'updated_at', 'created_by', 'updated_by', 
            'is_deleted', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = [
            'connection_status', 'last_sync_at', 'last_sync_log',
            'created_at', 'updated_at', 'created_by', 'updated_by', 
            'is_deleted', 'deleted_at', 'deleted_by','specific_provider_name'
        ]
class EmailModuleSettingsSerializer(serializers.ModelSerializer):
    available_merge_fields = serializers.SerializerMethodField()
    class Meta:
        model = EmailModuleSettings
        fields = [
            'imap_connection_status', 'enable_webhook_notifications', 'webhook_url',
            'enable_mail_merge', 'auto_generate_documents','attach_to_emails','document_storage_path', 'output_directory','available_merge_fields',
            'email_polling_interval_minutes', 'auto_categorization_enabled', 'fallback_tagging_enabled',
            'emails_per_page', 'auto_refresh_inbox', 'mark_read_on_open',
            'ai_intent_classification', 'ai_sentiment_analysis', 'ai_realtime_collaboration',
            'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at', 'deleted_by','available_merge_fields',]
    def get_available_merge_fields(self, obj):
        return [
            "{customerName}", "{policyNumber}", "{policyType}", 
            "{effectiveDate}", "{expiryDate}", "{premiumAmount}", 
            "{agentName}", "{companyName}"
        ]

class ClassificationRuleSerializer(serializers.ModelSerializer):
    keyword = serializers.CharField(required=False, max_length=100)
    class Meta:
        model = ClassificationRule
        fields = ['id', 'keyword', 'category', 'priority', 'is_enabled', 'created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at', 'deleted_by']
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'is_deleted', 'deleted_at', 'deleted_by']