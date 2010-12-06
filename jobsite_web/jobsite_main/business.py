"""
 Business rules and logic.
 Perzoot
"""

from jobsite_main.statics import *
from jobsite_main.search import Search




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
