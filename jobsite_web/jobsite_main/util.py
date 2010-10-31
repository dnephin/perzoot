"""
 Utility classes
"""

import simplejson
import solr
from datetime import datetime


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

