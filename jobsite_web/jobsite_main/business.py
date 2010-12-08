"""
 Business rules and logic.
 Perzoot
"""
import logging

from jobsite_main.statics import *
from jobsite_main.search import Search
from jobsite_main.db import get_user_events 


log = logging.getLogger('Business')

def get_search_type(request, form):
	"""
	Determine the search type from the request and form.
	"""
	if request.method == "POST":
		return CLEAN_SEARCH

	if 'event' in request.GET:
		return SEARCH_EVENT_SEARCH

	if form.cleaned_data.get('start'):
		return NEXT_PAGE_SEARCH

	if request.GET.get('otp_sort'):
		return RESORT_SEARCH

	if request.GET.get('otp_filter'):
		return FILTERED_SEARCH

	return CLEAN_SEARCH


def get_search_messages(form, response):
	"""
	Return a list of helpful search messages for this search based on
	the number of results and filters being used.
	"""



def suppliment_results(request, search_results):
	"""
	Remove postings that were deleted by the user and add identifiers for 
	visited/favorited postings for the user.
	"""
	if not search_results:
		return

	doc_map = dict((d['id'], d) for d in search_results['results'])

	user_events = get_user_events(request, ids=doc_map.keys())
	for event in user_events:
		if event.event == 'save':
			doc_map[event.posting_id]['type'] = 'saved_event'
			continue

		# Saved should overwrite opened
		if event.event == 'open' and not doc_map[event.posting_id]['type']:
			doc_map[event.posting_id]['type'] = 'opened_event'
			continue

		if event.event == 'remove':
			search_results['results'].remove(doc_map[event.posting_id])
			continue

		log.warn("Unknown user event type: %s" % (event.event))
		
