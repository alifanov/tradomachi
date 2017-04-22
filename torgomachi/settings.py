"""
Django settings for torgomachi project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import telebot

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lh5=r%-r+v4(ze*8)a84q(g2o&p#-w6x81#2h2m09f=^%*$4cf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api.apps.ApiConfig',
    'django_rq',
    'rest_framework',
    'push_notifications'
]

PUSH_NOTIFICATIONS_SETTINGS = {
    "APNS_CERTIFICATE": os.path.join(BASE_DIR, "certs", "pushSandbox.pem"),
    "APNS_TOPIC": "gateway.sandbox.push.apple.com",
    "APNS_USE_SANDBOX": True
}

APNS_USE_SANDBOX = True

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    }
}

TELEGRAM_TOKEN = '298399611:AAFJKjYtpkNL-mxd9mwB2tmrgDsSxW3liS4'

STICKER_WELCOME_FILE_ID = "CAADAgADEgADR_sJDB-1rNVHHuHMAg"
STICKER_BORN_FILE_ID = "CAADAgADLQADUNz6BejS0-HIEIfIAg"
STICKER_SUCCESS_FILE_ID = "CAADAgADVgADR_sJDBMAAeCty2eeNwI"
STICKER_FAIL_FILE_ID = "CAADAgADIwADR_sJDHGYlartjJK2Ag"
STICKER_SKIP_FILE_ID = "CAADAgADUAADR_sJDF_Z_SrDak8lAg"
STICKER_RIP_FILE_ID = "CAADAgADLgADUNz6BQYYbds717IGAg"
STICKER_OFFER_FILE_ID = "CAADAgADLgADUNz6BQYYbds717IGAg"

webhook_bot = telebot.TeleBot(TELEGRAM_TOKEN)

WEBHOOK_HOST = '107.170.43.198'
WEBHOOK_PORT = 443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = os.path.join(BASE_DIR, 'certs', 'webhook_cert.pem')
WEBHOOK_SSL_PRIV = os.path.join(BASE_DIR, 'certs', 'webhook_pkey.pem')

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/webhook/" % (TELEGRAM_TOKEN)

# print(WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

webhook_bot.remove_webhook()

webhook_bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'torgomachi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'torgomachi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
