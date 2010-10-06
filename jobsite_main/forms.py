from django.forms import *


class JobSearchForm(Form):
	"""
	Basic job posting search form.
	"""

	keywords = 	CharField(max_length=255)
	days =		IntegerField()
	city = 		CharField(max_length=200, initial='Montreal')



