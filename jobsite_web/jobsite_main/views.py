"""
 Perzoot Main - Views

"""

import logging

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpResponseServerError
from django.contrib.auth import logout as django_logout
from django.conf import settings

from jobsite_main.forms import JobSearchForm
from jobsite_main.search import Search 
from jobsite_main.util import DjangoJSONEncoder
from jobsite_main.db import *
from jobsite_main.helpers import service_friendly_name

import simplejson



log = logging.getLogger('View')

###############################################################################
#		Helpers	
###############################################################################

OK='ok'
ERROR='error'
NOTFOUND='notfound'
INPUT='input'

def json_response(request, code=OK, data=None):
	" Format the json response "

	resp = {'code': code, 'content': data}
	http_obj = HttpResponse

	if code == NOTFOUND:
		http_obj = HttpResponseNotFound
		resp['content'] = 'Page not found.'

	if code == ERROR:
		http_obj = HttpResponseServerError
		resp['content'] = 'Server error.'

	return http_obj(simplejson.dumps(resp, cls=DjangoJSONEncoder), 
			mimetype="application/json")


def handle_response(request, context={}, template=None, code=OK):
	"""
	 Handle the response by returned a full HTML page with header, or
	 just the AJAX data, if the request was an AJAX request.
	"""
	if request.method == 'GET' and request.GET.get('async'):
		return json_response(request, code, context)

	if code == NOTFOUND:
		return HttpResponseNotFound()

	if code == ERROR:
		return HttpResponseServerError()

	return render_to_response(template, context_instance=RequestContext(
			request, context))


###############################################################################
#		Actions
###############################################################################


def index(request):
	"""
	 Default landing page.  Contains a basic search form.
	"""
	# TODO: set session data to force the cookie (do i need to?)
	# TODO: Set city in city field of form
	form = JobSearchForm()
	return render_to_response('index.html', 
			context_instance=RequestContext(request, {'search_form': form}))



def search(request):
	"""
	Perform a search and return the data as JSON.
	"""
	form = JobSearchForm(request.GET)
	if not form.is_valid():
		# TODO: check for existing session and populate the form that way
		return handle_response(request, {'search_form': form}, 
				template='search.html', code=INPUT)

	resp = Search().search(form)

	return handle_response(request, 
			{'search_form': form, 'search_results': resp}, 'search.html')



def track_event(request, event_name, posting_id):
	"""
	Track a user performing an event relating to a job posting.
	"""
	user_id = request.user.id if request.user_.is_authenticated() else None
	session_id = request.session.session_key

	if db.save_user_event(event_name, posting_id, user_id, session_id):
		code = OK
	else:
		code = ERROR
	return json_response(request, code=code)



def static_page(request, page_name):
	"""
	Retrieve the contents for a (relatively) static page.
	"""
	page = load_static_page(page_name)
	if not page:
		return handle_response(request, code=NOTFOUND)

	return handle_response(request, {'page_data': page}, 
			template="static_page.html")



###############################################################################
#		Authentication Actions
###############################################################################

def logout(request):
	"""
	A simple request to check what the users auth status.
	Used to updated the user_block.
	"""
	django_logout(request)

	return handle_auth_block(request)


def handle_auth_block(request):
	"""
	Return the templated login block.
	"""
	return handle_response(request, {}, template='blocks/auth_block.html')


# TODO: can this be refactored to beter fit with the handlers ?
def auth_frame_wrapper(request, service):
	"""
	Return a page with a frame for login.
	"""

	if service not in settings.OAUTH_ACCESS_SETTINGS:
		return handle_response(request, code=NOTFOUND)

	if request.method == 'GET' and request.GET.get('async'):
		return json_response(request, data={
				'body': render_to_string('auth/frame.html', {'service': service}),
				'title': 'Login using %s' % service_friendly_name(service),
			})

	return handle_response(request, {'service': service}, 'auth/frame_wrapper.html')
