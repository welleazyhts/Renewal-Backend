"""
Production settings for Intelipro Insurance Policy Renewal System.
"""

from .base import *
from decouple import config
import sentry_sdk
import os
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

DEBUG = False

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,0.0.0.0,testserver,13.233.6.207',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 31536000 
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

X_FRAME_OPTIONS = 'DENY'

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 60,
    'options': '-c default_transaction_isolation=serializable',
    'sslmode': 'disable',
}

DATABASES['default']['CONN_MAX_AGE'] = 600

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'intelipro_renewal',
        'TIMEOUT': 300,
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

CELERY_TASK_ALWAYS_EAGER = False
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

LOGGING['handlers']['file']['level'] = 'WARNING'
LOGGING['handlers']['console']['level'] = 'ERROR'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['renewal_backend']['level'] = 'INFO'

LOGGING['handlers']['error_file'] = {
    'level': 'ERROR',
    'class': 'logging.FileHandler',
    'filename': config('ERROR_LOG_FILE', default='logs/error.log'),
    'formatter': 'verbose',
}

LOGGING['handlers']['security_file'] = {
    'level': 'INFO',
    'class': 'logging.FileHandler',
    'filename': config('SECURITY_LOG_FILE', default='logs/security.log'),
    'formatter': 'verbose',
}

LOGGING['loggers']['django.security'] = {
    'handlers': ['security_file', 'console'],
    'level': 'INFO',
    'propagate': False,
}

SENTRY_DSN = config('SENTRY_DSN', default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
                cache_spans=True,
            ),
            CeleryIntegration(
                monitor_beat_tasks=True,
                propagate_traces=True,
            ),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
        release=config('RELEASE_VERSION', default='1.0.0'),
    )

CONN_MAX_AGE = 600  

RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ADMIN_URL = config('ADMIN_URL', default='admin/')

print("🔒 Running in PRODUCTION mode")
print(f"🛡️  Security features enabled")
print(f"📊 Sentry monitoring: {'✅' if SENTRY_DSN else '❌'}")
print(f"💾 File storage: AWS S3")
print(f"🔐 SSL redirect: {SECURE_SSL_REDIRECT}")
 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = config("OPENAI_MODEL", default="gpt-4")
OPENAI_MAX_TOKENS = config("OPENAI_MAX_TOKENS", default=150, cast=int)
OPENAI_TEMPERATURE = config("OPENAI_TEMPERATURE", default=0.7, cast=float)

print("🤖 OpenAI Key Loaded:", "YES" if OPENAI_API_KEY else "NO")

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "renewal-backend-bucket"
AWS_S3_REGION_NAME = "ap-south-1"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
