"""
 Perzoot - settings.py
 Staging Environment.
"""

DEBUG = True
TEMPLATE_DEBUG = DEBUG
import os
PROJECT_ROOT = '/var/pz_stage/jobsite_web/'

import logging.config
logging.config.fileConfig('%s/logging.conf' % PROJECT_ROOT)

# Solr
SOLR_URL = 'http://localhost:8080/solr'


ADMINS = (
	('Perzoot Admin', 'admin@perzoot.com'),
)

MANAGERS = ADMINS

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'jobs',
		'USER': 'jobs',
		'PASSWORD': 'jobspass',
		'HOST': '',
		'PORT': '',
	}
}


# OAuth
OAUTH_ACCESS_SETTINGS = {
	'linkedin': {
		'keys': {
			'KEY':	  'OVWYIVnMYcNsaHsf3BRhzLMuaviknWiufpDrvJq_Cv5013547ezQioYZpZtZWeE8',
			'SECRET': 'Jk1yH4a4SvLysl3Ph__E9LIXp_lJgJ_M1DbXU3rj6oyV3ZJUaJqvcAvWu46h-y2H',
		},
		'endpoints': {
			'request_token': 'https://api.linkedin.com/uas/oauth/requestToken',
			'access_token': 'https://api.linkedin.com/uas/oauth/accessToken',
			'authorize': 'https://api.linkedin.com/uas/oauth/authorize',
			'provider_scope':'',
			'callback': 'jobsite_main.oauth_callbacks.linked_in',
		},
	},
}


# Locale
TIME_ZONE = 'America/Montreal'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True

MEDIA_ROOT = PROJECT_ROOT + '/media/'
MEDIA_URL = '/m/'
ADMIN_MEDIA_PREFIX = '/m/admin/'
SECRET_KEY = '129e12jnakfm23rjf90JIKN@uf4niq2n3fk129jfkn9jf9jrf2300;.'
ROOT_URLCONF = 'urls'
SESSION_COOKIE_AGE = 6 * 7 * 24 * 60 * 60 	# 6 weeks
LOGIN_URL = '/login'

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#	 'django.template.loaders.eggs.Loader',
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
	'jobsite_main',
	'oauth_access',
)

