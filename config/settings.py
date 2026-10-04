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
# MEDIA / CLOUD STORAGE — Neon Object Storage (S3-compatible)
# =============================================================================
# Neon Object Storage S3 protokolini qo'llab-quvvatlaydi.
# Render da deploy qilinganda rasmlar o'chib ketmasligi uchun kerak.
#
# Render Dashboard → Environment Variables da quyidagilarni o'rnating:
#   NEON_STORAGE_ENDPOINT   — masalan: https://us-east-1.storage.neon.tech
#   NEON_STORAGE_ACCESS_KEY — Access Key ID
#   NEON_STORAGE_SECRET_KEY — Secret Access Key
#   NEON_STORAGE_BUCKET     — Bucket nomi

NEON_STORAGE_ENDPOINT   = os.environ.get('NEON_STORAGE_ENDPOINT')
NEON_STORAGE_ACCESS_KEY = os.environ.get('NEON_STORAGE_ACCESS_KEY')
NEON_STORAGE_SECRET_KEY = os.environ.get('NEON_STORAGE_SECRET_KEY')
NEON_STORAGE_BUCKET     = os.environ.get('NEON_STORAGE_BUCKET')

_use_neon_storage = all([
    NEON_STORAGE_ENDPOINT,
    NEON_STORAGE_ACCESS_KEY,
    NEON_STORAGE_SECRET_KEY,
    NEON_STORAGE_BUCKET,
])

if _use_neon_storage:
    # --- Neon Object Storage (S3-compatible) ---
    INSTALLED_APPS += ['storages']

    # boto3 / S3 sozlamalari
    AWS_S3_ENDPOINT_URL       = NEON_STORAGE_ENDPOINT
    AWS_ACCESS_KEY_ID         = NEON_STORAGE_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY     = NEON_STORAGE_SECRET_KEY
    AWS_STORAGE_BUCKET_NAME   = NEON_STORAGE_BUCKET
    AWS_S3_REGION_NAME        = os.environ.get('NEON_STORAGE_REGION', 'us-east-1')

    # Fayllar public o'qilishi uchun
    AWS_DEFAULT_ACL            = 'public-read'
    AWS_QUERYSTRING_AUTH       = False   # URL larda ?AWSAccessKeyId=... bo'lmasin
    AWS_S3_FILE_OVERWRITE      = False   # Bir xil nomli fayl ustiga yozilmasin
    AWS_S3_OBJECT_PARAMETERS   = {'CacheControl': 'max-age=86400'}  # 1 kun kesh

    # Media fayllar (yuklangan rasmlar) uchun
    MEDIA_URL = f'{NEON_STORAGE_ENDPOINT}/{NEON_STORAGE_BUCKET}/media/'

    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': {
                'location': 'media',   # bucket ichida media/ papkasiga joylaydi
            },
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
