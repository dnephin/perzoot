"""
 Views for job search.

"""

import logging

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

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




# Ajax
import simplejson

OK='ok'
ERROR='error'

class ExJSONEncoder(simplejson.JSONEncoder):

	def default(self, o):
		try:
			return simplejson.JSONEncoder.default(self, o);
		except TypeError:
			return ""



def json_response(request, code=OK, data=None, message=None):
	" Format the json response "

	resp = {'code': code, 'message': message, 'content': data}
	return HttpResponse(simplejson.dumps(resp, cls=ExJSONEncoder), mimetype="application/json")



def search(request):
	"""
	Perform a search and return the data as JSON.
	"""
	form = JobSearchForm(request.GET)
	form.is_valid()
	resp = Search().search(form).results
	return json_response(request, data=resp)
