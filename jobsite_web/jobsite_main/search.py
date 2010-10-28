"""
 Search module for jobsite_web app.

"""

import solr
from django.conf import settings
from datetime import datetime
import string
import simplejson
import logging


log = logging.getLogger('Search')

SOLR_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

solr_conn = solr.SolrConnection(settings.SOLR_URL)


class SolrJSONEncoder(simplejson.JSONEncoder):
	"""
	 A JSON encoder which has been extended to encode Solr Response 
	 objects and datetime objects.
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
		else:
			return simplejson.JSONEncoder.default(self, o);


#TODO: query with json output format
class Search(object):
	"""
	 Perform a search from a django form.
	"""
	

	def search(self, search_form):
		"""
		Perform a search.
		"""
		params = self.build_query(search_form.cleaned_data)
		r = solr_conn.query(**params)
		return r




	def build_query(self, data):
		"""
		 Build a query and params for performing a solr query.
		"""
		q_parts = []
		q_parts.append(self.handle_keywords(data.get('keywords')))
		q_parts.append(self.handle_days(data.get('days')))
		q_parts.append(self.handle_city(data.get('city')))

		return {
			'q': " AND ".join(q_parts),
			'sort': self.handle_sort(data.get('sort')),
			'sort_order': 'desc',
			'start': data.get('start', 0),
			'rows': data.get('rows', 20),
		}



	def handle_keywords(self, kws):
		if not kws:
			return ""

		return "body: (%s)" % " OR ".join(map(string.lower, kws.split()))
		

	def handle_days(self, days):
		if not days:
			return ""
		return "date: [NOW-%dDAY TO NOW]" % days


	def handle_city(self, city):
		if not city:
			return ""
		return "city: %s" % city.lower()


	def handle_sort(self, sort):
		if not sort:
			return "date, id"
		if sort not in ('date', 'relevency'):
			log.warn("Unknown sort type: %s" % (sort)) 
			return "date, id"
		return sort
