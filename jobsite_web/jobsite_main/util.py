"""
 Utility classes
"""

import simplejson
import solr
from datetime import datetime
from django.conf import settings


class DjangoJSONEncoder(simplejson.JSONEncoder):
	"""
	 A JSON encoder which has been extended to encode Solr Response 
	 objects, datetime objects, and any object with a __json__ method.
	 """

	def default(self, o):

		if isinstance(o, solr.Response):
			return {
				'results': o.results,
				'start': o.results.start,
				'numFound': o.results.numFound,
				}
		elif isinstance(o, datetime):
			return o.strftime('%Y-%m-%dT%H-%M-%S')
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
