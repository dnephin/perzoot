"""
 Perzoot
 
 Database abstraction layer.
"""

from jobsite_web.jobsite_main.models import *
from django.core.exceptions import ObjectDoesNotExist
import logging

log = logging.getLogger('DB')


def save_user_event(event_name, posting_id, user_id, session_id):
	"""
	Save a user event object.
	"""
	ue = UserEvent(session_id, user_id, posting_id, event_name)
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
