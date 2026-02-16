from .base import *
from decouple import config
from django.conf import settings

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,0.0.0.0,testserver,13.233.6.207',
    cast=lambda v: [s.strip() for s in v.split(',')],
    
)
ALLOWED_HOSTS.append('.ngrok-free.dev')
ALLOWED_HOSTS.append('overgrossly-sugarlike-xuan.ngrok-free.dev')
INSTALLED_APPS += [
    
]

if DEBUG:
    INSTALLED_APPS += [
    ]

if not settings.EMAIL_HOST_USER:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    print("📧 Using console email backend (emails will appear in terminal)")
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    print("📧 Using SMTP email backend (emails will be sent via SMTP)")

CORS_ALLOW_ALL_ORIGINS = True

SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 60,  
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}


CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default=False, cast=bool)
CELERY_TASK_EAGER_PROPAGATES = True

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'


LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['renewal_backend']['level'] = 'DEBUG'

if not config('AWS_ACCESS_KEY_ID', default=None):
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

print("🚀 Running in DEVELOPMENT mode")
print(f"📊 Debug mode: {DEBUG}")
print(f"🔗 Allowed hosts: {ALLOWED_HOSTS}")
print(f"📧 Email backend: {EMAIL_BACKEND}")
print(f"💾 File storage: {DEFAULT_FILE_STORAGE if 'DEFAULT_FILE_STORAGE' in locals() else 'AWS S3'}") 