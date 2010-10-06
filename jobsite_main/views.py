"""
 Views for job search.

"""

import logging

from django.shortcuts import render_to_response
from django.template import RequestContext

from jobsite_main.forms import JobSearchForm
from jobsite_main.search import Search


log = logging.getLogger('View')


def index(request):
	"""
	Index page with simple search form.
	"""
	
	if request.method == 'POST':
		form = JobSearchForm(request.POST)
		if form.is_valid():
			log.debug('Search form is valid.')
			resp = Search().search(form)

			return render_to_response('index.html', 
					context_instance=RequestContext(request, {
					'response': resp, 'form': form}))

	else:
		form = JobSearchForm()

	return render_to_response('index.html', 
			context_instance=RequestContext(request, {'form': form}))


