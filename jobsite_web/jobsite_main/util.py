"""
 Utility classes
"""

import simplejson
import solr
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_backends
from django.db.models.query import QuerySet


class DjangoJSONEncoder(simplejson.JSONEncoder):
	"""
	 A JSON encoder which has been extended to encode Solr Response 
	 objects, datetime objects, and any object with a __json__ method.
	 """

	def default(self, o):

		if isinstance(o, datetime):
			return o.strftime('%Y-%m-%dT%H-%M-%S')
		if isinstance(o, QuerySet):
			return list(o)
		elif hasattr(o, '__json__'):
			return o.__json__()
		else:
			return simplejson.JSONEncoder.default(self, o);




def service_friendly_name(service):
	"""
	Return the human readable name of a service from settings.
	"""
	return settings.OAUTH_ACCESS_SETTINGS[service].get(
			'friendly_name', service)


def to_json(obj):
	""" Encode the obj as a JSON string. """
	return simplejson.dumps(obj, cls=DjangoJSONEncoder)



def auto_authenticate(user):
	"""
	Authenticate a user without a password.  This method is a substitute for 
	django.contrib.auth.authenticate.  It sets the users backend without
	requiring a password.  This is being used for OAuth and forcing login
	after registration.
	"""
	for backend in get_backends():
		if backend.get_user(user.id):
			user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
			return user
