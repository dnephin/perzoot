"""
 Perzoot Main - Views

"""

import logging

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpResponseServerError
from django.contrib.auth import logout as django_logout, login as django_login
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.forms import ValidationError

from jobsite_main.forms import JobSearchForm, UserForm
from jobsite_main.search import Search 
from jobsite_main.db import *
from jobsite_main.util import service_friendly_name, to_json, auto_authenticate



log = logging.getLogger('View')

###############################################################################
#		Helpers	
###############################################################################

# The login request was successful (2xx)
OK			= 'ok'
# The request was successful but the data submitted was incorrect (2xx)
INPUT		= 'input'
# The request was successful but the action requires a login (2xx)
LOGIN		= 'login'
# A requested object could not be found (4xx)
NOTFOUND	= 'notfound'
# There was a server side error (5xx)
ERROR		= 'error'


def is_async(request):
	"""
	If the page was sent with the async flag set to 1, return True,
	otherwise return False.
	"""
	return (request.method == 'GET' and request.GET.get('async', False))

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

	return http_obj(to_json(resp), mimetype="application/json")


def handle_response(request, context={}, template=None, code=OK):
	"""
	 Handle the response by returned a full HTML page with header, or
	 just the AJAX data, if the request was an AJAX request.
	"""
	if is_async(request):
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
	save_search(request, form)

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
#		User/Authentication Actions
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


def auth_frame_wrapper(request, service):
	"""
	Return a page with a frame for login.
	"""

	if service not in settings.OAUTH_ACCESS_SETTINGS:
		return handle_response(request, code=NOTFOUND)

	if is_async(request):
		return json_response(request, data={
				'body': render_to_string('auth/frame.html', {'service': service}),
				'title': 'Login using %s' % service_friendly_name(service),
			})

	return handle_response(request, {'service': service}, 'auth/frame_wrapper.html')


@login_required
def user_view(request):
	"""
	Display the user view page that lets users update their profile.
	"""
	user_form = UserForm(instance=request.user)
	return render_to_response('user_page.html', context_instance=RequestContext(
			request, {'user_form': user_form}))


@login_required
def user_field_update(request):
	"""
	Validate, and update an individual account setting.
	"""
	if (request.method != 'GET' or not request.GET.get('field') or
			not request.GET.get('value')):
		return json_response(request, code=ERROR)

	field = request.GET.get('field')
	value = request.GET.get('value')
	user = request.user

	if not hasattr(user, field):
		return json_response(request, ERROR)
		
	# special case for password, has to be set using this method to hash it
	if field == 'password':
		user.set_password(value)
	else:
		setattr(user, field, value)

	try:
		user.clean_fields()
	except ValidationError, e:
		return json_response(request, INPUT, e.message_dict[field])

	user.save()
	
	return json_response(request)
	


def login(request):
	"""
	Display the login for, and log the user in.
	"""

	if is_async(request):
		# Login form submited
		if request.GET.get('submit', False):
			form = AuthenticationForm(data=request.GET)
			if form.is_valid():
				django_login(request, form.get_user())
				return json_response(request)
			
		else:
			form = AuthenticationForm()

		return json_response(request, code=INPUT, data=
					render_to_string('blocks/login.html', {'form': form}))

	# TODO: login without javascript


def register(request):
	"""
	Display the registration form, and save the user.
	"""

	if is_async(request):
		if request.GET.get('submit', False):
			form = UserForm(data=request.GET)
			if form.is_valid():
				user = form.save()
				auto_authenticate(user)
				django_login(request, user)
				return json_response(request)
		else:
			form = UserForm()
			
		return json_response(request, code=INPUT, data=
					render_to_string('blocks/register.html', {'form': form}))
	

	# TODO: register without javascript

