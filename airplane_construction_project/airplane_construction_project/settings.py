"""
Django settings for airplane_construction_project project.
"""

import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=d(h9sjyr67e(+k_i+!vqfd$(c_$y1curw!n1a26#&lx&4z-%4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',  # Swagger
    'django_filters',
    'django_minio_backend.apps.DjangoMinioBackendConfig',
    'bmstu_lab',
]

# Исправленная конфигурация MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',  # ← ЗАКОММЕНТИРОВАНО (не нужно, т.к. CSRF отключён в кастомном классе)
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'airplane_construction_project.urls'

# Исправленная конфигурация TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'airplane_construction_project.wsgi.application'

# ========== БАЗА ДАННЫХ POSTGRESQL ==========
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'airplane_project',
        'USER': 'postgres',
        'PASSWORD': 'postgres123',
        'HOST': 'localhost',
        'PORT': '5455',
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ========== НАСТРОЙКИ MINIO ==========

# Базовые параметры для подключения
MINIO_ENDPOINT = 'localhost:9000'
MINIO_ACCESS_KEY = 'minioadmin'
MINIO_SECRET_KEY = 'minioadmin123'
MINIO_USE_HTTPS = False
MINIO_REGION = 'us-east-1'

# Названия ваших бакетов
MINIO_STATIC_BUCKET = 'django-static'
MINIO_MEDIA_BUCKET = 'django-media'

# --- СТРУКТУРА STORAGES ---
STORAGES = {
    # Хранилище для статических файлов (CSS, JS)
    "staticfiles": {
        "BACKEND": "django_minio_backend.models.MinioBackendStatic",
        "OPTIONS": {
            "MINIO_ENDPOINT": MINIO_ENDPOINT,
            "MINIO_ACCESS_KEY": MINIO_ACCESS_KEY,
            "MINIO_SECRET_KEY": MINIO_SECRET_KEY,
            "MINIO_USE_HTTPS": MINIO_USE_HTTPS,
            "MINIO_REGION": MINIO_REGION,
            "MINIO_STATIC_FILES_BUCKET": MINIO_STATIC_BUCKET,
            "MINIO_CONSISTENCY_CHECK_ON_START": True,
            "MINIO_URL_EXPIRY_HOURS": timedelta(days=1),
        },
    },
    # Хранилище по умолчанию (для медиафайлов и загрузок пользователей)
    "default": {
        "BACKEND": "django_minio_backend.models.MinioBackend",
        "OPTIONS": {
            "MINIO_ENDPOINT": MINIO_ENDPOINT,
            "MINIO_ACCESS_KEY": MINIO_ACCESS_KEY,
            "MINIO_SECRET_KEY": MINIO_SECRET_KEY,
            "MINIO_USE_HTTPS": MINIO_USE_HTTPS,
            "MINIO_REGION": MINIO_REGION,
            "MINIO_DEFAULT_BUCKET": MINIO_MEDIA_BUCKET,
            "MINIO_PUBLIC_BUCKETS": [MINIO_STATIC_BUCKET],
            "MINIO_PRIVATE_BUCKETS": [MINIO_MEDIA_BUCKET],
            "MINIO_CONSISTENCY_CHECK_ON_START": True,
            "MINIO_URL_EXPIRY_HOURS": timedelta(days=7),
            "MINIO_BUCKET_CHECK_ON_SAVE": True,
        },
    },
}

# Настройка STATIC_URL и MEDIA_URL для использования MinIO
STATIC_URL = f'http://{MINIO_ENDPOINT}/{MINIO_STATIC_BUCKET}/'
MEDIA_URL = f'http://{MINIO_ENDPOINT}/{MINIO_MEDIA_BUCKET}/'

# Пути для локальной разработки
STATICFILES_DIRS = [
    BASE_DIR / 'airplane_construction_project/static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

print(f"Static files will be served from: {STATIC_URL}")
print(f"Media files will be served from: {MEDIA_URL}")

# MinIO настройки для загрузки файлов
DEFAULT_FILE_STORAGE = 'django_minio_backend.models.MinioBackend'
MINIO_DEFAULT_BUCKET = 'django-media'

# ========== НАСТРОЙКИ DRF (С КАСТОМНЫМ КЛАССОМ БЕЗ CSRF) ==========
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'bmstu_lab.authentication.CsrfExemptSessionAuthentication',  # Кастомный класс без CSRF
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# ========== НАСТРОЙКИ SWAGGER ==========
LOGIN_URL = None  # Отключаем редирект на /accounts/login/ для Swagger

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,  # Включает редактор JSON
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch',
    ],
}

# ========== ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ==========
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
]

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'