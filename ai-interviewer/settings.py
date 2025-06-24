import os,sys
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment-based .env file if it exists
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

# Add apps dir to path
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-gdu&(&8i^5b9*pns81d%t*ndnr7)hnca=)2&rc_aex4gmh7-)q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    # If DEBUG, default hosts are localhost, 127.0.0.1, and [::1].
]


# Application definition

INSTALLED_APPS = [
    # Project apps
    'profiles.apps.ProfilesConfig',
    'documents.apps.DocumentsConfig',
    'jobs.apps.JobsConfig',
    'locations.apps.LocationsConfig',
    'users.apps.UsersConfig',
    'transcripts.apps.TranscriptsConfig',
    'core.apps.CoreConfig',
    'interviews.apps.InterviewsConfig',
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes', 
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # External apps
    "django_browser_reload",
    'rest_framework',
    'drf_spectacular',
    'drf_spectacular_sidecar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = 'ai-interviewer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
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

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

WSGI_APPLICATION = 'ai-interviewer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Frontend config settings

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Pairwise API',
    'DESCRIPTION': 'Internal API for Pairwise',
    'VERSION': '0.0.1',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',  
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

OPENAI_API_KEY = os.getenv("OPENAI-API-KEY")


# for sending calendly invitation email. 
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'PUT_SENDER_GMAIL_HERE'                # my gmail
EMAIL_HOST_PASSWORD = 'GOOGLE_APP_PASSWORD_HERE'  # get it from https://myaccount.google.com/apppasswords.  
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
