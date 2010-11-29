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

solr_conn = solr.Solr(settings.SOLR_URL)


class Search(object):
	"""
	 Perform a search from a django form.
	"""

	SEARCH_FACETS = ('category', 'domain', 'company')


	def retrieve_titles(self, ids):
		"""
		Retrieve a set of posting titles for the ids.
		"""
		handler = solr.SearchHandler(solr_conn, wt='python')
		return handler(fl=['id', 'title'], q="id: (%s)" % (" OR ".join(map(str, ids))))
	

	def search(self, search_form):
		"""
		Perform a search.
		"""
		params = self.build_query(search_form.cleaned_data)
		params.update(self.build_facets())

		params['sort'] = self.handle_sort(search_form.cleaned_data.get('sort')),
		params['qf'] = "title^2 body"

		handler = solr.SearchHandler(solr_conn, wt='python')
		r = handler(**params)
		return r


	def build_query(self, data):
		"""
		 Build a query and params for performing a solr query.
		"""
		q_parts = []
		q_parts.append(self.handle_keywords(data.get('keywords')))
		q_parts.append(self.handle_days(data.get('days')))
		q_parts.append(self.handle_city(data.get('city')))
		for filter in self.SEARCH_FACETS: 
			part = self.handle_filter(filter, data.get('filter_' + filter))
			if part:
				q_parts.append(part)

		return {
			'q': " AND ".join(q_parts),
			'start': data.get('start', 0),
			'rows': data.get('rows', 20),
		}


	def build_facets(self):
		"""
		Build search query facets parameters.
		"""
		return {
			'facet': 'true',
			'facet_field': self.SEARCH_FACETS, 
			'facet_sort': 'true',
			'facet_limit': 10,
			'facet_mincount': 2,
			'facet_missing': 'true',
			# dates
			'facet_date': 'date',
			'facet_date_end': 'NOW',
			'facet_date_start': 'NOW/DAY-10DAYS',
			'facet_date_gap': '+1DAY',
		}



	def handle_filter(self, filter, values):
		if not values:
			return ""

		return "-%s: (%s)" % (filter, " OR ".join(map(lambda v: '"%s"' % v, values)))

	def handle_keywords(self, kws):
		if not kws:
			return ""

		keywords = " OR ".join(map(string.lower, kws.split()))
		return "body: (%s) title: (%s)" % (keywords, keywords)
		

	def handle_days(self, days):
		if not days:
			return ""
		return "date: [NOW-%dDAY TO NOW]" % days


	def handle_city(self, city):
		if not city:
			return ""
		return "city: %s" % city.lower()


	DEFAULT_SORT = 'date desc, score desc'

	def handle_sort(self, sort):
		if not sort or sort == 'date':
			return self.DEFAULT_SORT
		if sort == 'relevancy':
			return "score desc"
		else:
			log.warn("Unknown sort type: %s" % (sort)) 
		return self.DEFAULT_SORT
