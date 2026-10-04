"""
Django settings for config project.
Production and Local compatible configuration.
"""

import os
from pathlib import Path
import dj_database_url

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-9^*+m+mvqm)^8d7v(ozona158^-qgf2#w!2srm1a(hb4z%n1uc'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')

allowed_hosts_raw = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,.onrender.com')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_raw.split(',') if h.strip()]

csrf_trusted_raw = os.environ.get('CSRF_TRUSTED_ORIGINS', 'https://*.onrender.com')
CSRF_TRUSTED_ORIGINS = [c.strip() for c in csrf_trusted_raw.split(',') if c.strip()]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'philosophers',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Production static files serving
    'config.middleware.SecurityHeadersMiddleware',  # CSP nonce va xavfsizlik headerlari
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.csp_nonce',  # CSP nonce barcha template'larga
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Production PostgreSQL (Render, Supabase yoki Neon)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Lokal rivojlanish uchun SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'uz-uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# MEDIA / CLOUD STORAGE — S3-compatible (Supabase Storage, Neon, AWS S3)
# =============================================================================
STORAGE_ENDPOINT   = (
    os.environ.get('SUPABASE_STORAGE_ENDPOINT') or
    os.environ.get('AWS_ENDPOINT_URL_S3') or
    os.environ.get('NEON_STORAGE_ENDPOINT') or
    os.environ.get('AWS_S3_ENDPOINT_URL')
)
STORAGE_ACCESS_KEY = (
    os.environ.get('SUPABASE_STORAGE_ACCESS_KEY') or
    os.environ.get('AWS_ACCESS_KEY_ID') or
    os.environ.get('NEON_STORAGE_ACCESS_KEY')
)
STORAGE_SECRET_KEY = (
    os.environ.get('SUPABASE_STORAGE_SECRET_KEY') or
    os.environ.get('AWS_SECRET_ACCESS_KEY') or
    os.environ.get('NEON_STORAGE_SECRET_KEY')
)
STORAGE_BUCKET     = (
    os.environ.get('SUPABASE_STORAGE_BUCKET') or
    os.environ.get('AWS_STORAGE_BUCKET_NAME') or
    os.environ.get('NEON_STORAGE_BUCKET') or
    'media'
)
STORAGE_REGION     = (
    os.environ.get('SUPABASE_STORAGE_REGION') or
    os.environ.get('AWS_REGION') or
    os.environ.get('NEON_STORAGE_REGION') or
    'ap-southeast-2'
)

_use_cloud_storage = all([
    STORAGE_ENDPOINT,
    STORAGE_ACCESS_KEY,
    STORAGE_SECRET_KEY,
    STORAGE_BUCKET,
])

if _use_cloud_storage:
    INSTALLED_APPS += ['storages']

    # S3 sozlamalari
    AWS_S3_ENDPOINT_URL       = STORAGE_ENDPOINT
    AWS_ACCESS_KEY_ID         = STORAGE_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY     = STORAGE_SECRET_KEY
    AWS_STORAGE_BUCKET_NAME   = STORAGE_BUCKET
    AWS_S3_REGION_NAME        = STORAGE_REGION

    # S3-compatible provayderlar (Supabase / Neon) path-style addressing talab qiladi
    AWS_S3_ADDRESSING_STYLE    = 'path'

    # Supabase / Neon ACL larni qo'llab-quvvatlamaydi (AccessControlListNotSupported xatosi bo'lmasligi uchun)
    AWS_DEFAULT_ACL            = None
    AWS_QUERYSTRING_AUTH       = False   # URL larda imzo tokenlari bo'lmasin
    AWS_S3_FILE_OVERWRITE      = False   # Bir xil nomli fayl ustiga yozilmasin
    AWS_S3_OBJECT_PARAMETERS   = {'CacheControl': 'max-age=86400'}  # 1 kun kesh

    # Supabase CDN uchun public URL domeni
    # Masalan: https://<ref>.storage.supabase.co/storage/v1/s3 -> <ref>.supabase.co/storage/v1/object/public/<bucket>
    import re
    sb_match = re.search(r'https?://([^.]+)\.(?:storage\.)?supabase\.co', STORAGE_ENDPOINT)
    if sb_match:
        project_ref = sb_match.group(1)
        s3_custom_domain = f"{project_ref}.supabase.co/storage/v1/object/public/{STORAGE_BUCKET}"
    else:
        s3_custom_domain = os.environ.get('AWS_S3_CUSTOM_DOMAIN')

    storage_options = {
        'addressing_style': 'path',
        'default_acl': None,
        'querystring_auth': False,
    }

    if s3_custom_domain:
        AWS_S3_CUSTOM_DOMAIN = s3_custom_domain
        MEDIA_URL = f"https://{s3_custom_domain}/"
        storage_options['custom_domain'] = s3_custom_domain
    else:
        MEDIA_URL = f"{STORAGE_ENDPOINT.rstrip('/')}/{STORAGE_BUCKET}/"

    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': storage_options,
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
else:
    # Lokal muhit — oddiy fayl tizimi (env variables o'rnatilmagan)
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }


# Email (lokal muhitda console ga chiqaradi, production'da .env orqali SMTP o'rnatiladi)
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# Auth redirects
LOGIN_REDIRECT_URL = 'learn'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'signup'

# Admin faollashtirish maxfiy kaliti (Render Free da Shell bo'lmaganda)
# MUHIM: .env faylida ADMIN_SETUP_SECRET o'rnatilmasa, xususiyat o'chiq bo'ladi.
ADMIN_SETUP_SECRET = os.environ.get('ADMIN_SETUP_SECRET')


# =============================================================================
# XAVFSIZLIK SOZLAMALARI (Production)
# =============================================================================

# Render HTTPS ni load balancer darajasida hal qiladi.
# Django'ga X-Forwarded-Proto headerini HTTPS belgisi sifatida tanishtirish:
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    # HSTS: brauzerga faqat HTTPS orqali muloqot qilishni buyuradi (2 yil)
    SECURE_HSTS_SECONDS = 63072000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Cookie'larni faqat HTTPS orqali yuborish
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Cookie'larni JavaScript dan himoya qilish
    SESSION_COOKIE_HTTPONLY = True

    # SameSite: CSRF hujumlaridan qo'shimcha himoya
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'
