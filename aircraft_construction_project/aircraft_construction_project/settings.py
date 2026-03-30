"""
Django settings for aircraft_construction_project project.
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
    'django_minio_backend.apps.DjangoMinioBackendConfig',
]

# Исправленная конфигурация MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Должен быть до AuthenticationMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aircraft_construction_project.urls'

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

WSGI_APPLICATION = 'aircraft_construction_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Пути для локальной разработки
STATICFILES_DIRS = [
    BASE_DIR / 'aircraft_construction_project/static',
]

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


if STORAGES["staticfiles"]["BACKEND"] == "django_minio_backend.models.MinioBackendStatic":
    # Django будет использовать MinIO для статики
    STATIC_URL = f'http://{MINIO_ENDPOINT}/{MINIO_STATIC_BUCKET}/'
    print(f"Static files will be served from: {STATIC_URL}")
else:
    STATIC_URL = '/static/'