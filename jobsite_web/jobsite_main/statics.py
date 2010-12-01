"""
	String statics

"""

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



### Types of searches

# This search was performed with no filters, and new terms
CLEAN_SEARCH		= "clean_search"
# This search was performed to retrieve additional results
NEXT_PAGE_SEARCH	= "next_page_search"
# This search was performed by changing filters
FILTERED_SEARCH		= "filtered_search"
# This search was performed by changing sort
RESORT_SEARCH		= "resort_search"
# This search was performed from a saved search
SEARCH_EVENT_SEARCH	= "search_event_search"
