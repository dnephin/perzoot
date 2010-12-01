"""
 Business rules and logic.
 Perzoot
"""

from jobsite_main.statics import *
from jobsite_main.search import Search




def get_search_type(request, form):
	"""
	Determine the search type from the request and form.

	FIXME: Note that due to the order of resort/filter, some filters may end up
	counting as resorts. 
	"""
	if request.method == "POST":
		return CLEAN_SEARCH

	if 'event' in request.GET:
		return SEARCH_EVENT_SEARCH

	if form.cleaned_data.get('start'):
		return NEXT_PAGE_SEARCH

	if form.cleaned_data.get('sort'):
		return RESORT_SEARCH

	for filter in Search.SEARCH_FACETS:
		if form.cleaned_data.get('filter_' + filter):
			return FILTERED_SEARCH

	return CLEAN_SEARCH


def get_search_messages(form, response):
	"""
	Return a list of helpful search messages for this search based on
	the number of results and filters being used.
	"""
