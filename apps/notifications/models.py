from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel, TimestampedModel
from apps.customers.models import Customer
from apps.policies.models import Policy
from apps.campaigns.models import Campaign
import uuid
import json

User = get_user_model()

class NotificationChannel(BaseModel):
    CHANNEL_TYPE_CHOICES = [
        ('in_app', 'In-App Notification'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
    ]
    
    name = models.CharField(max_length=100)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPE_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)
    
    configuration = models.JSONField(default=dict)
    rate_limit_per_minute = models.PositiveIntegerField(default=60)
    rate_limit_per_hour = models.PositiveIntegerField(default=1000)
    
    total_sent = models.PositiveIntegerField(default=0)
    total_delivered = models.PositiveIntegerField(default=0)
    total_failed = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'notification_channels'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.channel_type})"

class NotificationTemplate(BaseModel):
    """Notification templates"""
    TEMPLATE_TYPE_CHOICES = [
        ('policy_renewal', 'Policy Renewal'),
        ('payment_due', 'Payment Due'),
        ('claim_update', 'Claim Update'),
        ('campaign_response', 'Campaign Response'),
        ('system_alert', 'System Alert'),
        ('user_mention', 'User Mention'),
        ('task_assignment', 'Task Assignment'),
        ('report_ready', 'Report Ready'),
        ('custom', 'Custom Template'),
    ]
    
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    email_subject_template = models.CharField(max_length=200, blank=True)
    email_body_template = models.TextField(blank=True)
    sms_template = models.CharField(max_length=160, blank=True)
    push_title_template = models.CharField(max_length=100, blank=True)
    push_body_template = models.CharField(max_length=200, blank=True)
    
    variables = models.JSONField(default=list, help_text="List of template variables")
    
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#007bff')
    
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'notification_templates'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"

class Notification(BaseModel):
    NOTIFICATION_TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('urgent', 'Urgent'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='info')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    recipient_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_notifications')
    recipient_customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='received_notifications')
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    
    policy = models.ForeignKey(Policy, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    template_variables = models.JSONField(default=dict, blank=True)
    
    channels = models.JSONField(default=list, help_text="List of channels to send notification")
    
    scheduled_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    action_url = models.URLField(blank=True, help_text="URL to redirect when notification is clicked")
    action_data = models.JSONField(default=dict, blank=True)
    
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, blank=True)
    image_url = models.URLField(blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient_user', 'status']),
            models.Index(fields=['recipient_customer', 'status']),
            models.Index(fields=['priority', 'created_at']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        recipient = self.recipient_user or self.recipient_customer or self.recipient_email
        return f"{self.title} to {recipient}"

class NotificationDelivery(BaseModel):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='deliveries')
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=Notification.STATUS_CHOICES, default='pending')
    
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    external_id = models.CharField(max_length=200, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'notification_deliveries'
        unique_together = ['notification', 'channel']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification.title} via {self.channel.name} - {self.status}"

class NotificationPreference(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    enabled = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    preferences = models.JSONField(default=dict)
    digest_frequency = models.CharField(max_length=20, choices=[
        ('none', 'No Digest'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
    ], default='none')
    
    push_token = models.TextField(blank=True, help_text="FCM/APNs push token")
    device_tokens = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.get_full_name()}"

class NotificationGroup(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    users = models.ManyToManyField(User, blank=True, related_name='notification_groups')
    customers = models.ManyToManyField(Customer, blank=True, related_name='notification_groups')
    
    default_channels = models.JSONField(default=list)
    priority = models.CharField(max_length=20, choices=Notification.PRIORITY_CHOICES, default='normal')
    
    membership_rules = models.JSONField(default=dict, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'notification_groups'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class NotificationRule(BaseModel):
    TRIGGER_TYPE_CHOICES = [
        ('policy_expiry', 'Policy Expiry'),
        ('payment_due', 'Payment Due'),
        ('claim_status_change', 'Claim Status Change'),
        ('campaign_response', 'Campaign Response'),
        ('user_login', 'User Login'),
        ('system_event', 'System Event'),
        ('schedule', 'Scheduled'),
        ('custom', 'Custom Trigger'),
    ]
    
    name = models.CharField(max_length=200)
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    conditions = models.JSONField(default=dict)
    
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    channels = models.JSONField(default=list)
    priority = models.CharField(max_length=20, choices=Notification.PRIORITY_CHOICES, default='normal')
    
    recipient_type = models.CharField(max_length=20, choices=[
        ('policy_holder', 'Policy Holder'),
        ('assigned_user', 'Assigned User'),
        ('user_group', 'User Group'),
        ('notification_group', 'Notification Group'),
        ('custom', 'Custom Recipients'),
    ])
    
    recipient_groups = models.ManyToManyField(NotificationGroup, blank=True)
    custom_recipients = models.JSONField(default=list, blank=True)
    
    delay_minutes = models.PositiveIntegerField(default=0)
    
    max_frequency = models.CharField(max_length=20, choices=[
        ('once', 'Once Only'),
        ('daily', 'Once Per Day'),
        ('weekly', 'Once Per Week'),
        ('unlimited', 'Unlimited'),
    ], default='once')
    
    is_active = models.BooleanField(default=True)
    trigger_count = models.PositiveIntegerField(default=0)
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'notification_rules'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.trigger_type})"

class NotificationBatch(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    total_notifications = models.PositiveIntegerField(default=0)
    sent_notifications = models.PositiveIntegerField(default=0)
    failed_notifications = models.PositiveIntegerField(default=0)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_duration = models.PositiveIntegerField(null=True, blank=True)
    
    batch_size = models.PositiveIntegerField(default=100)
    delay_between_batches = models.PositiveIntegerField(default=60, help_text="Delay in seconds")
    
    error_message = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'notification_batches'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.status}"

class NotificationLog(BaseModel):
    ACTION_CHOICES = [
        ('created', 'Notification Created'),
        ('sent', 'Notification Sent'),
        ('delivered', 'Notification Delivered'),
        ('read', 'Notification Read'),
        ('clicked', 'Notification Clicked'),
        ('failed', 'Notification Failed'),
        ('expired', 'Notification Expired'),
        ('dismissed', 'Notification Dismissed'),
    ]
    
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    channel = models.ForeignKey(NotificationChannel, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    details = models.JSONField(default=dict, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'notification_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['notification', 'action']),
            models.Index(fields=['action', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.notification.title}"

class NotificationSubscription(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    
    endpoint = models.URLField()
    p256dh_key = models.TextField()
    auth_key = models.TextField()
    
    device_type = models.CharField(max_length=20, choices=[
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
    ], blank=True)
    
    browser = models.CharField(max_length=50, blank=True)
    user_agent = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notification_subscriptions'
        unique_together = ['user', 'endpoint']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Push subscription for {self.user.get_full_name()}"

class NotificationDigest(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_digests')
    digest_type = models.CharField(max_length=20, choices=[
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
    ])
    
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    notifications = models.ManyToManyField(Notification, related_name='digests')
    summary = models.JSONField(default=dict)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'notification_digests'
        unique_together = ['user', 'digest_type', 'period_start']
        ordering = ['-period_start']
    
    def __str__(self):
        return f"{self.digest_type} digest for {self.user.get_full_name()} - {self.period_start.date()}" 