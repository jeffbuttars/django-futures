"""
Django settings for dj project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from django.conf import global_settings

PROJECT_NAME = 'dj'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^n%8c*kis1594axpst%o#ihebn@6b-*rd0+gbw1bu2silu73!8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = DEBUG

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'jquery.context_processor.jquery_url',
    'usethis_bootstrap.context_processor.bootstrap_urls',
)


LOGIN_REDIRECT_URL = "/"
ALLOWED_HOSTS = ['.*']

# Application definition
INSTALLED_APPS = (
    'django.contrib.auth',
    'django_admin_bootstrapped.bootstrap3',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_futures',
    'jquery',
    'usethis_bootstrap',
    'core',
    'test',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'dj.urls'
WSGI_APPLICATION = 'dj.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '%(levelname)s: %(filename)s:%(lineno)s %(module)s::'
                '%(funcName)s() '
                '%(asctime)s %(process)s '
                '%(message)s'),
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        # 'file_all': {
        #     'level': 'DEBUG',
        #     'class': 'logging.FileHandler',
        #     'formatter': 'verbose',
        #     'filename': _log_dir + '/django.log',
        # },
    },
    'loggers': {

        'django': {
            # 'handlers': ['console', 'file_all'],
            'handlers': ['console'],
            # 'level': (DEBUG and 'DEBUG') or 'INFO',
            'level': 'ERROR',
            'propagate': True,
        },

        'django.request': {
            # 'handlers': ['mail_admins', 'console', 'file_all'],
            # 'handlers': ['mail_admins', 'console'],
            'handlers': ['console'],
            # 'level': (DEBUG and 'DEBUG') or 'ERROR',
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.debug': {
            'handlers': ['console', 'file_all'],
            'handlers': ['console'],
            # 'level': (DEBUG and 'DEBUG') or 'INFO',
            'level': 'DEBUG',
            'propagate': False,
        },
        PROJECT_NAME: {
            # 'handlers': ['console', 'file_all'],
            'handlers': ['console'],
            'level': (DEBUG and 'DEBUG') or 'INFO',
            'propagate': True,
        }
    }
}
