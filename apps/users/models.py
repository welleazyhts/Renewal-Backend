from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid
class UserManager(BaseUserManager):    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class Role(models.Model):    
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=dict, help_text="Permission mappings for this role")
    is_system = models.BooleanField(default=False, help_text="System roles cannot be deleted")
    default_permissions = models.JSONField(default=dict, blank=True, help_text="Factory default permissions for reset")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_role'
        ordering = ['name']
        
    def __str__(self):
        return self.display_name
    
    @property
    def permission_list(self):
        if isinstance(self.permissions, list):
            return self.permissions
        elif isinstance(self.permissions, dict):
            return list(self.permissions.keys())
        else:
            return []
    
    def has_permission(self, permission):
        if isinstance(self.permissions, list):
            return permission in self.permissions
        elif isinstance(self.permissions, dict):
            return self.permissions.get(permission, False)
        else:
            return False


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, db_index=True)
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    department = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending Activation'),
    ]

    DEPARTMENT_CHOICES = [
        ('claims_processing', 'Claims Processing'),
        ('underwriting', 'Underwriting'),
        ('customer_service', 'Customer Service'),
        ('sales_marketing', 'Sales & Marketing'),
        ('it', 'Information Technology'),
        ('finance_accounting', 'Finance & Accounting'),
        ('legal_compliance', 'Legal & Compliance'),
        ('management', 'Management'),
        ('other', 'Other'),
    ]
    department = models.CharField(
        max_length=100, 
        choices=DEPARTMENT_CHOICES, 
        blank=True,
        default='other'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    force_password_change = models.BooleanField(default=False)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=255, blank=True)
    backup_tokens = models.JSONField(default=list, blank=True)
    
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)
    
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='light'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['role']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def initials(self):
        return f"{self.first_name[:1]}{self.last_name[:1]}".upper()
    
    def has_permission(self, permission):
        if self.is_superuser:
            return True
        if not self.role:
            return False
        return self.role.has_permission(permission)
    
    def get_permissions(self):
        if self.is_superuser:
            return ['*'] 
        if not self.role:
            self.assign_default_role()
            if self.role:
                return self.role.permission_list
            return []
        return self.role.permission_list
    
    def assign_default_role(self):
        if not self.role:
            try:
                default_role = Role.objects.get(name='agent')
                self.role = default_role
                self.save(update_fields=['role'])
                return True
            except Role.DoesNotExist:
                try:
                    default_role = Role.objects.first()
                    if default_role:
                        self.role = default_role
                        self.save(update_fields=['role'])
                        return True
                except Exception:
                    pass
        return False
    
    def is_account_locked(self):
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False
    
    def unlock_account(self):
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])
    
    def record_login_attempt(self, success=True, ip_address=None):
        if success:
            self.failed_login_attempts = 0
            self.locked_until = None
            self.last_login_ip = ip_address
            self.last_activity = timezone.now()
            self.login_count += 1
        else:
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= 5:
                self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        
        self.save(update_fields=[
            'failed_login_attempts', 'locked_until', 'last_login_ip',
            'last_activity', 'login_count'
        ])


class UserSession(models.Model):    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def extend_session(self, minutes=60):
        self.expires_at = timezone.now() + timezone.timedelta(minutes=minutes)
        self.last_activity = timezone.now()
        self.save(update_fields=['expires_at', 'last_activity'])


class UserPreference(models.Model):    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    dashboard_config = models.JSONField(default=dict, blank=True)
    notification_settings = models.JSONField(default=dict, blank=True)
    ui_settings = models.JSONField(default=dict, blank=True)
    filter_presets = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} preferences"


class PasswordResetToken(models.Model):    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Password reset for {self.user.email}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def mark_as_used(self, ip_address=None):
        self.is_used = True
        self.used_at = timezone.now()
        self.ip_address = ip_address
        self.save(update_fields=['is_used', 'used_at', 'ip_address']) 