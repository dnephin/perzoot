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

# Name of the value in the session that stores the id of the last search event
LAST_SEARCH_EVENT = 'last_search_event'
