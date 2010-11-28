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
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from jobsite_main.forms import JobSearchForm, UserForm
from jobsite_main.search import Search, SOLR_DATE_FORMAT
from jobsite_main import db
from jobsite_main.util import service_friendly_name, to_json, auto_authenticate
from jobsite_main.util import from_json 
from jobsite_main.statics import *

from datetime import datetime


log = logging.getLogger('View')

###############################################################################
#		Helpers	
###############################################################################


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


def format_search(sr):
	"""
	Format the solr response object into a view object.

	sr - a solr response formated as python dict (wt=python).
	"""
	# TODO: highlighting
	resp = {
		'header': {
			'qtime': sr['responseHeader']['QTime'],
			'numFound': sr['response']['numFound'],
			'start': sr['response']['start'],
		},
		'filters': {'Date': {}},
		'results': [],
	}
	
	for field, value_list in sr['facet_counts']['facet_fields'].iteritems():
		field = field.capitalize()
		resp['filters'][field] = {}
		for i in range(0, len(value_list)/2, 2):
			name = value_list[i] or 'missing'
			resp['filters'][field][name] = value_list[i+1]

	for date, value in sr['facet_counts']['facet_dates']['date'].iteritems():
		if date.find('T00:00:00Z') < 0:
			continue
		resp['filters']['Date'][format_date(date)] = value

	for doc in sr['response']['docs']:
		new_doc = {
			'id': doc['id'],
			'title': doc['title'],
			'url':   doc['url'],
			'details': build_details(doc),
			'summary': doc['summary'],
			'date': format_date(doc['date']),
			'source': doc['domain'],
		}
		resp['results'].append(new_doc)

	log.debug('Search response: %s' % (resp))
	return resp
		
def format_date(date_string):
	"""
	Convert a date string (in solr default format) to a standard
	visual representation.
	"""
	return datetime.strptime(date_string, SOLR_DATE_FORMAT
			).strftime('%b %d')


FORMAT_MAP = {
	'salary': lambda s: "$%s/yr" % (s),
	'wage':   lambda s: "$%s/hr" % (s),
	'recruiter': lambda s: "recruiter" if s else "",
}

def build_details(doc):
	"""
	Build the details string from a solr document.
	"""
	detail_list = []
	for key in ('category', 'industry', 'company', 'location', 'type', 
			'salary', 'wage', 'email', 'phone', 'level', 'recruiter'):
		if key not in doc:
			continue

		if key in FORMAT_MAP:
			value = FORMAT_MAP[key](doc[key])
		else:
			value = doc[key]
		detail_list.append(value)
	return ",".join(detail_list)



###############################################################################
#		Actions
###############################################################################


def index(request):
	"""
	If no searches exist for this session or user, redirect to main
	otherwise post to search with last search populated.
	"""
	last_search = db.get_search_history(request, limit=1)
	if last_search:
		return redirect(reverse('jobsite_main.views.search'))
	return redirect(reverse('jobsite_main.views.main'))


def main(request):
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

	The data for the search even can be retrieve in 3 ways, in this order:
	 - if the 'event' param is present, retrieve that event and use that for data
	 - if there is GET or POST data, use that for data
	 - if there is a previous search, retreive it, and use that for data
	"""

	form = None
	if request.method == "GET" and 'event' in request.GET:
		search_event = db.get_search_history(request, ids=[request.GET['event']])[:1]
		if search_event:
			form = JobSearchForm(from_json(search_event[0].full_string))

	if not form:
		form_data = request.GET if request.method == "GET" else request.POST
		if form_data:
			form = JobSearchForm(form_data)

	if not form:
		last_search = db.get_search_history(request, limit=1)
		if last_search:
			form = JobSearchForm(from_json(last_search[0].full_string))

	if not form:
		form = JobSearchForm()

	if not form.is_valid():
		return handle_response(request, {'search_form': form}, 
				template='search.html', code=INPUT)

	resp = Search().search(form)
	# TODO: restrict saving of search on some conditions (such as repeating a
	# previous search, or filtering)
	search_event = db.save_search_event(request, form)
	request.session[LAST_SEARCH_EVENT] = search_event

	return handle_response(request, {
			'search_form': form, 
			'search_results': format_search(resp),
			'search_event': search_event.id,
			'search_type': form.cleaned_data.get('sort', 'date'),
			}, 'search.html')


def search_history(request, saved=False):
	"""
	Retrieve the search history.
	"""
	return json_response(request, data={
			'list': db.get_search_history(request, saved)
	})

def favorite_postings(request):
	"""
	Retrieve the favorite postings for the user.
	"""

	posting_list = db.get_user_events(request, type='save', sorted=True, limit=10)
	if len(posting_list) < 1:
		return json_response(request, data={'list': None})
	titles = Search().retrieve_titles(map(lambda u: u.posting_id, posting_list))

	posting_map = dict(map(lambda p: (p.posting_id, p),posting_list))

	resp = []
	for doc in titles['response']['docs']:
		resp.append({
			'id': doc['id'], 
			'terms': doc['title'],
			'date': posting_map[doc['id']].tstamp.strftime('%b %d')
		})

	return json_response(request, data={'list': resp})

	

def save_search(request):
	"""
	Save the last search.
	"""
	if request.method != 'GET' or 'id' not in request.GET:
		return json_response(request, code=ERROR)

	db.save_search(int(request.GET['id']))

	return json_response(request)


def track_event(request, event_name, posting_id):
	"""
	Track a user performing an event relating to a job posting.
	"""
	user = request.user if request.user.is_authenticated() else None
	session_id = request.session.session_key

	if db.save_user_event(event_name, posting_id, user, session_id):
		code = OK
	else:
		code = ERROR
	return json_response(request, code=code)



def static_page(request, page_name):
	"""
	Retrieve the contents for a (relatively) static page.
	"""
	page = db.load_static_page(page_name)
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

