
from django.conf import settings


def service_friendly_name(service):
	"""
	Return the human readable name of a service from settings.
	"""
	return settings.OAUTH_ACCESS_SETTINGS[service].get(
			'friendly_name', service)
