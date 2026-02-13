from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
class EmailTemplateTag(models.Model):    
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#6c757d', help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_email_template_tags')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_email_template_tags')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_email_template_tags')
    
    class Meta:
        db_table = 'email_template_tags'
        ordering = ['name']
        verbose_name = 'Email Template Tag'
        verbose_name_plural = 'Email Template Tags'
    
    def __str__(self):
        return self.name


class EmailTemplate(models.Model):    
    TEMPLATE_TYPE_CHOICES = [
        ('html', 'HTML'),
        ('text', 'Plain Text'),
        ('both', 'Both HTML and Text'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    
    html_content = models.TextField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    template_type = models.CharField(max_length=10, choices=TEMPLATE_TYPE_CHOICES, default='both')
    
    variables = models.JSONField(default=dict, blank=True, help_text="Available variables for this template")
    
    tags = models.ManyToManyField(EmailTemplateTag, blank=True, related_name='templates')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True, help_text="Available to all users")
    
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_email_templates')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_email_templates')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_email_templates')
    
    class Meta:
        db_table = 'email_templates'
        ordering = ['-created_at']
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
        indexes = [
            models.Index(fields=['status', 'is_public']),
            models.Index(fields=['created_by', 'status']),
        ]
    
    def __str__(self):
        return self.name
    
    def increment_usage(self):
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.status = 'archived'
        self.save(update_fields=['is_deleted', 'deleted_at', 'status'])
    
    def render_content(self, context: dict = None) -> dict:
        if context is None:
            context = {}
        
        rendered = {
            'subject': self.subject,
            'html_content': self.html_content,
            'text_content': self.text_content
        }
        
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            rendered['subject'] = rendered['subject'].replace(placeholder, str(value))
            if rendered['html_content']:
                rendered['html_content'] = rendered['html_content'].replace(placeholder, str(value))
            if rendered['text_content']:
                rendered['text_content'] = rendered['text_content'].replace(placeholder, str(value))
        
        return rendered


class EmailTemplateVersion(models.Model):    
    id = models.BigAutoField(primary_key=True)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=500)
    html_content = models.TextField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    template_type = models.CharField(max_length=10, choices=EmailTemplate.TEMPLATE_TYPE_CHOICES)
    variables = models.JSONField(default=dict, blank=True)
    
    change_summary = models.TextField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_email_template_versions')
    
    class Meta:
        db_table = 'email_template_versions'
        ordering = ['-version_number']
        unique_together = ['template', 'version_number']
        verbose_name = 'Email Template Version'
        verbose_name_plural = 'Email Template Versions'
    
    def __str__(self):
        return f"{self.template.name} v{self.version_number}"
    
    def save(self, *args, **kwargs):
        if not self.version_number:
            last_version = EmailTemplateVersion.objects.filter(
                template=self.template
            ).order_by('-version_number').first()
            self.version_number = (last_version.version_number + 1) if last_version else 1
        
        if self.is_current:
            EmailTemplateVersion.objects.filter(
                template=self.template
            ).exclude(id=self.id).update(is_current=False)
        
        super().save(*args, **kwargs)
