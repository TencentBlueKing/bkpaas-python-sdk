import base64
import os

BASE_DIR = os.getcwd()

MEDIA_URL = '/media/'

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
SECRET_KEY = 'nosecretatall'
USE_TZ = True

# Extra settings
BKKRILL_ENCRYPT_SECRET_KEY = base64.b64encode(b'\x01' * 32)

PAAS_SERVICE_PROVIDER_CLS = 'paas_service.base_vendor.DummyProvider'
PAAS_SERVICE_JWT_CLIENTS = [
    {
        "iss": "paas-v3",
        "key": "67d8e22749764a339d794aa8b6bb1a94",
        "algorithm": "HS256",
    },
]
PAAS_SERVICE_SVC_INSTANCE_RENDER_FUNC = 'paas_service.models.render_instance_data'

LANGUAGE_CODE = 'zh-cn'

LANGUAGES = [("zh-cn", "简体中文"), ("en", "English")]

ROOT_URLCONF = 'tests.urls'
STATIC_URL = '/static/'
DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'paas_service',
]
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Append middlewares from paas_service to make client auth works
    'paas_service.auth.middleware.VerifiedClientMiddleware',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
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
