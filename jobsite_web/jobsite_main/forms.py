from django.forms import *


class JobSearchForm(Form):
	"""
	Basic job search form.
	"""

	keywords = 	CharField(max_length=255)
	days =		IntegerField()
	city = 		CharField(max_length=200, initial='Montreal')
	start =		IntegerField(widget=HiddenInput, initial=0, required=False)
	rows = 		IntegerField(widget=HiddenInput, initial=20, required=False)


	def clean_rows(self):
		rows = self.cleaned_data['rows']
		if not rows:
			return 20
		return rows

	def clean_start(self):
		start = self.cleaned_data['start']
		if not start:
			return 0
		return start
