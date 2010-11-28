"""
 Perzoot
 
 Database abstraction layer.
"""

from jobsite_main.models import *
from jobsite_main.util import to_json
from django.core.exceptions import ObjectDoesNotExist
import simplejson
import logging

log = logging.getLogger('DB')


def save_user_event(event_name, posting_id, user, session_id):
	"""
	Save a user event object.
	"""
	ue = UserEvent(session=session_id, user=user, 
			posting_id=posting_id, event=event_name)
	try:
		ue.save()
	except BaseException, e:
		log.warn('Failed to save UserEvent (%s): %s' % (ue, e))
		return False
	return True


def load_static_page(page_name):
	" Load the static content page. "

	try:
		page = SitePage.objects.filter(page__exact=page_name, 
				active__exact=True).order_by('-version')[0]
	except (IndexError, ObjectDoesNotExist), err:
		log.warn('Failed to find page %s: %s' % (page_name, err))
		return False
	return page


def save_search_event(request, search_form):
	" Save a search event. "

	user = request.user if not request.user.is_anonymous() else None

	s = SearchEvent(
		session = request.session.session_key,
		user_id = user,
		terms = search_form.cleaned_data.get('keywords'),
		full_string = to_json(search_form)
	)
	s.save()
	return s


def save_search(event_id):
	" Update a search as saved. "
	SearchEvent.objects.filter(id=event_id).update(saved=True)


def get_search_history(request, saved=False, ids=None, limit=10):
	" Retrieve the search history for this user, or for their session. "

	user = request.user if not request.user.is_anonymous() else None
	if user:
		selector = {'user_id': user}
	else:
		selector = {'session': request.session.session_key}

	if saved:
		selector['saved'] = True

	if ids:
		selector['id__in'] = ids

	searches = SearchEvent.objects.filter(**selector).order_by('-tstamp')[:limit]
	return searches


def get_user_events(request, type=None, ids=None, sorted=False, limit=None):
	"""
	Retrieve a list of user events for a user.
	"""
	user = request.user if request.user.is_authenticated() else None

	if user:
		selector = {'user': user}
	else:
		selector = {'session': request.session.session_key}

	if type:
		selector['event'] = type

	if ids:
		selector['posting_id__in'] = ids

	query = UserEvent.objects.filter(**selector)

	if sorted:
		query = query.order_by('-tstamp')
	
	if limit:
		query = query[:limit]

	return query
