from rest_framework import serializers
from apps.renewals.models import RenewalCase
from .models import WhatsAppMessage
from apps.templates.models import Template
from django.utils import timezone
import pytz

class WhatsAppMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField() 
    
    class Meta:
        model = WhatsAppMessage
        fields = [
            'id', 'sender_type', 'sender_name', 'message_type', 
            'content', 'media_url', 'timestamp', 'is_read', 'is_starred'
        ]
        read_only_fields = ['sender_type', 'sender_name', 'timestamp', 'is_read', 'is_starred']

    def get_sender_name(self, obj):
        if obj.sender_type == 'agent' and obj.sender_user:
            return obj.sender_user.first_name
            
        elif obj.sender_type == 'customer':
            try:
                return obj.case.customer.full_name
            except AttributeError:
                return "Unknown Customer"
        return obj.sender_type.title()

    def get_timestamp(self, obj):
        local_tz = pytz.timezone('Asia/Kolkata') 
        local_dt = obj.created_at.astimezone(local_tz)
        return local_dt.strftime("%I:%M %p")

class WhatsAppChatListSerializer(serializers.ModelSerializer):
    case_id = serializers.CharField(source='case_number', read_only=True)
    
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    customer_avatar = serializers.CharField(source='customer.avatar', read_only=True, default=None)
    
    policy_number = serializers.CharField(source='policy.policy_number', read_only=True)
    
    status = serializers.CharField(read_only=True) 
    priority = serializers.CharField(read_only=True)
    
    days_left = serializers.SerializerMethodField()
    renewal_date = serializers.DateField(source='policy.end_date', read_only=True)
    
    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = RenewalCase
        fields = [
            'case_id', 'customer_name', 'customer_phone', 'customer_avatar',
            'policy_number', 'status', 'priority', 
            'days_left', 'renewal_date',
            'last_message', 'last_message_time', 'unread_count'
        ]

    def get_days_left(self, obj):
        if obj.policy and obj.policy.end_date:
            delta = obj.policy.end_date - timezone.now().date()
            return delta.days
        return 0

    def get_last_message(self, obj):
        last_msg = obj.whatsapp_messages.last()
        if last_msg:
            return last_msg.content[:50] + "..." if len(last_msg.content) > 50 else last_msg.content
        return "Start the conversation..."

    def get_last_message_time(self, obj):
        last_msg = obj.whatsapp_messages.last()
        if last_msg:
            return last_msg.created_at.strftime("%I:%M %p")
        return ""

    def get_unread_count(self, obj):
        return obj.whatsapp_messages.filter(sender_type='customer', is_read=False).count()


class StartNewChatSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    customer_name = serializers.CharField()
    policy_number = serializers.CharField()
    premium_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    renewal_date = serializers.DateField()
    initial_message = serializers.CharField(
        required=True, 
        error_messages={"required": "You must send an initial message to start the chat."}
    )

class WhatsAppTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['id', 'name', 'content']