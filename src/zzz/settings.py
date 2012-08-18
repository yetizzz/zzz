# Django settings for zzz project.
import os
import dj_database_url


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
_ = lambda x: os.path.join(ROOT_DIR, x)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': dj_database_url.config(default='sqlite:///' + _('database.db'))
}

SENTRY_DSN = os.getenv('SENTRY_DSN', None)
REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = _('media')
MEDIA_URL = '/media/'
STATIC_ROOT = _('media/static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = '(yk1ujh))^l7e6(t6j-bgc7$@(4v_@1pbohfpck7og-a5u8#v&amp;'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'analytics.middleware.VisitMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'zzz.urls'
WSGI_APPLICATION = 'zzz.wsgi.application'

TEMPLATE_DIRS = (
    _('templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'tastypie',
    'hydra',
    'gunicorn',
    'analytics',
)

if not SENTRY_DSN is None:
    INSTALLED_APPS += ('raven.contrib.django',)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
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
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
