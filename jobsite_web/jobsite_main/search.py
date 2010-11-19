"""
 Search module for jobsite_web app.

 Performs search and handles response from solr.
"""

import solr
from django.conf import settings
from datetime import datetime
import string
import logging


log = logging.getLogger('Search')

SOLR_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

solr_conn = solr.SolrConnection(settings.SOLR_URL)


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
		params.update(self.build_facets())
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


	def build_facets(self):
		"""
		Build search query facets.
		"""
		return {
			'facet': 'true',
			'facet.field': 'category',
			'facet.field': 'city',
			'facet.field': 'domain',
			'facet.field': 'company',
			'facet.sort': 'true',
			'facet.limit': 10,
			'facet.mincount': 2,
			'facet.missing': 'true'
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
