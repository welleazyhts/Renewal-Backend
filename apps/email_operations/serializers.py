from rest_framework import serializers
from .models import EmailMessage, EmailQueue, EmailTracking, EmailDeliveryReport, EmailAnalytics
from django.utils import timezone
class EmailMessageSerializer(serializers.ModelSerializer):    
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    
    class Meta:
        model = EmailMessage
        fields = [
            'id', 'message_id', 'to_emails', 'cc_emails', 'bcc_emails',
            'from_email', 'from_name', 'reply_to', 'subject', 'html_content',
            'text_content', 'template_id', 'template_name', 'template_variables',
            'priority', 'priority_display', 'status', 'status_display',
            'scheduled_at', 'sent_at', 'campaign_id', 'tags', 'provider_name',
            'provider_message_id', 'error_message', 'retry_count', 'max_retries',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
            'updated_by', 'updated_by_name', 'is_deleted', 'deleted_at', 'deleted_by'
        ]
        read_only_fields = [
            'id', 'message_id', 'sent_at', 'provider_name', 'provider_message_id',
            'error_message', 'retry_count', 'created_at', 'updated_at',
            'created_by', 'updated_by', 'is_deleted', 'deleted_at', 'deleted_by'
        ]


class EmailMessageCreateSerializer(serializers.ModelSerializer):    
    class Meta:
        model = EmailMessage
        fields = [
            'to_emails', 'cc_emails', 'bcc_emails', 'from_email', 'from_name',
            'reply_to', 'subject', 'html_content', 'text_content', 'template_id',
            'template_variables', 'priority', 'scheduled_at', 'campaign_id', 'tags'
        ]
    
    def create(self, validated_data):
        import uuid
        validated_data['message_id'] = str(uuid.uuid4())
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class EmailMessageUpdateSerializer(serializers.ModelSerializer):    
    class Meta:
        model = EmailMessage
        fields = [
            'to_emails', 'cc_emails', 'bcc_emails', 'from_email', 'from_name',
            'reply_to', 'subject', 'html_content', 'text_content', 'template_id',
            'template_variables', 'priority', 'scheduled_at', 'campaign_id', 'tags'
        ]
    
    def update(self, instance, validated_data):
        """Update an email message"""
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class EmailQueueSerializer(serializers.ModelSerializer):    
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    email_message_data = EmailMessageSerializer(source='email_message', read_only=True)
    
    class Meta:
        model = EmailQueue
        fields = [
            'id', 'email_message', 'email_message_data', 'priority', 'priority_display',
            'status', 'status_display', 'scheduled_for', 'processed_at', 'attempts',
            'max_attempts', 'error_message', 'last_error', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'processed_at', 'attempts', 'error_message', 'last_error',
            'created_at', 'updated_at'
        ]


class EmailTrackingSerializer(serializers.ModelSerializer):    
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    email_message_subject = serializers.CharField(source='email_message.subject', read_only=True)
    email_message_to = serializers.CharField(source='email_message.to_emails', read_only=True)
    
    class Meta:
        model = EmailTracking
        fields = [
            'id', 'email_message', 'email_message_subject', 'email_message_to',
            'event_type', 'event_type_display', 'event_data', 'ip_address',
            'user_agent', 'location', 'link_url', 'link_text', 'event_time'
        ]
        read_only_fields = ['id', 'event_time']


class EmailDeliveryReportSerializer(serializers.ModelSerializer):    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    email_message_subject = serializers.CharField(source='email_message.subject', read_only=True)
    email_message_to = serializers.CharField(source='email_message.to_emails', read_only=True)
    
    class Meta:
        model = EmailDeliveryReport
        fields = [
            'id', 'email_message', 'email_message_subject', 'email_message_to',
            'provider_name', 'provider_message_id', 'status', 'status_display',
            'status_message', 'response_time', 'raw_data', 'reported_at'
        ]
        read_only_fields = ['id', 'reported_at']


class EmailAnalyticsSerializer(serializers.ModelSerializer):    
    period_type_display = serializers.CharField(source='get_period_type_display', read_only=True)
    
    class Meta:
        model = EmailAnalytics
        fields = [
            'id', 'date', 'period_type', 'period_type_display', 'campaign_id',
            'template_id', 'emails_sent', 'emails_delivered', 'emails_opened',
            'emails_clicked', 'emails_bounced', 'emails_complained',
            'emails_unsubscribed', 'delivery_rate', 'open_rate', 'click_rate',
            'bounce_rate', 'complaint_rate', 'unsubscribe_rate',
            'avg_response_time', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'delivery_rate', 'open_rate', 'click_rate', 'bounce_rate',
            'complaint_rate', 'unsubscribe_rate', 'created_at', 'updated_at'
        ]


class BulkEmailSerializer(serializers.Serializer):    
    to_emails = serializers.ListField(
        child=serializers.EmailField(),
        help_text="List of recipient email addresses"
    )
    subject = serializers.CharField(max_length=500)
    html_content = serializers.CharField(required=False, allow_blank=True)
    text_content = serializers.CharField(required=False, allow_blank=True)
    template_id = serializers.UUIDField(required=False, allow_null=True)
    template_variables = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        default=dict
    )
    from_email = serializers.EmailField(required=False)
    from_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    reply_to = serializers.EmailField(required=False, allow_blank=True)
    cc_emails = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        default=list
    )
    bcc_emails = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        default=list
    )
    priority = serializers.ChoiceField(
        choices=EmailMessage.PRIORITY_CHOICES,
        default='normal'
    )
    scheduled_at = serializers.DateTimeField(required=False, allow_null=True)
    campaign_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )


class ScheduledEmailSerializer(serializers.Serializer):    
    to_emails = serializers.EmailField()
    subject = serializers.CharField(max_length=500)
    html_content = serializers.CharField(required=False, allow_blank=True)
    text_content = serializers.CharField(required=False, allow_blank=True)
    template_id = serializers.UUIDField(required=False, allow_null=True)
    template_variables = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        default=dict
    )
    from_email = serializers.EmailField(required=False)
    from_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    reply_to = serializers.EmailField(required=False, allow_blank=True)
    cc_emails = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        default=list
    )
    bcc_emails = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        default=list
    )
    priority = serializers.ChoiceField(
        choices=EmailMessage.PRIORITY_CHOICES,
        default='normal'
    )
    scheduled_at = serializers.DateTimeField()
    campaign_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )


class EmailStatsSerializer(serializers.Serializer):    
    total_emails = serializers.IntegerField()
    sent_emails = serializers.IntegerField()
    delivered_emails = serializers.IntegerField()
    failed_emails = serializers.IntegerField()
    pending_emails = serializers.IntegerField()
    delivery_rate = serializers.FloatField()
    open_rate = serializers.FloatField()
    click_rate = serializers.FloatField()
    bounce_rate = serializers.FloatField()
    avg_response_time = serializers.FloatField()
    emails_by_status = serializers.DictField()
    emails_by_priority = serializers.DictField()
    emails_by_campaign = serializers.DictField()
    recent_activity = serializers.ListField()


class EmailCampaignStatsSerializer(serializers.Serializer):    
    campaign_id = serializers.CharField()
    campaign_name = serializers.CharField()
    total_emails = serializers.IntegerField()
    sent_emails = serializers.IntegerField()
    delivered_emails = serializers.IntegerField()
    opened_emails = serializers.IntegerField()
    clicked_emails = serializers.IntegerField()
    bounced_emails = serializers.IntegerField()
    complained_emails = serializers.IntegerField()
    unsubscribed_emails = serializers.IntegerField()
    delivery_rate = serializers.FloatField()
    open_rate = serializers.FloatField()
    click_rate = serializers.FloatField()
    bounce_rate = serializers.FloatField()
    complaint_rate = serializers.FloatField()
    unsubscribe_rate = serializers.FloatField()
    avg_response_time = serializers.FloatField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()


class SentEmailListSerializer(serializers.ModelSerializer):    
    sent_time = serializers.SerializerMethodField()
    created_time = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()
    priority_text = serializers.SerializerMethodField()
    sender_info = serializers.SerializerMethodField()
    recipient_count = serializers.SerializerMethodField()
    class Meta:
        model = EmailMessage
        fields = [
            'id', 'message_id', 'subject', 'sender_info', 'to_emails', 
            'recipient_count', 'status_text', 'priority_text', 'sent_time', 
            'created_time', 'content_preview', 'provider_name', 'provider_message_id'
        ]
    
    def get_sent_time(self, obj):
        if obj.sent_at:
            return obj.sent_at.strftime('%Y-%m-%d %H:%M:%S')
        return None
    
    def get_created_time(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return None
    
    def get_content_preview(self, obj):
        content = obj.text_content or obj.html_content or ''
        import re
        clean_content = re.sub(r'<[^>]+>', '', content)
        return clean_content[:100] + '...' if len(clean_content) > 100 else clean_content
    
    def get_status_text(self, obj):
        status_map = {
            'sent': 'Sent Successfully',
            'delivered': 'Delivered',
            'failed': 'Failed',
            'pending': 'Pending',
            'bounced': 'Bounced',
            'complained': 'Complained'
        }
        return status_map.get(obj.status, obj.status.title())
    
    def get_priority_text(self, obj):
        priority_map = {
            'low': 'Low Priority',
            'normal': 'Normal Priority',
            'high': 'High Priority',
            'urgent': 'Urgent'
        }
        return priority_map.get(obj.priority, obj.priority.title())
    
    def get_sender_info(self, obj):
        if obj.from_name:
            return f"{obj.from_name} <{obj.from_email}>"
        return obj.from_email
    
    def get_recipient_count(self, obj):
        count = 1  
        if obj.cc_emails:
            count += len(obj.cc_emails)
        if obj.bcc_emails:
            count += len(obj.bcc_emails)
        return count
