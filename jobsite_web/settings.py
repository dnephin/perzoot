"""
 Perzoot - settings.py
 Development Environment.
"""

DEBUG = True
TEMPLATE_DEBUG = DEBUG
import os
PROJECT_ROOT = os.getcwd()


# Solr
SOLR_URL = 'http://localhost:8080/solr'


ADMINS = (
	('Perzoot Admin', 'dnephin@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': 'jobs',
        'PASSWORD': 'jobspass',
        'HOST': '',
        'PORT': '',
    }
}


# Locale
TIME_ZONE = 'America/Montreal'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True

MEDIA_ROOT = PROJECT_ROOT + '/media/'
MEDIA_URL = '/m/'
ADMIN_MEDIA_PREFIX = '/media_admin/'
SECRET_KEY = '129e12jnakfm23rjf90JIKN@uf4niq2n3fk129jfkn9jf9jrf2300;.'
ROOT_URLCONF = 'jobsite_web.urls'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
#	'django.middleware.cache.UpdateCacheMiddleware',

	# Adds to Vary header
#	'django.middleware.gzip.GZipMiddleware',
#	'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

#	'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_DIRS = (
	PROJECT_ROOT + '/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
)

