"""
	Forms
"""

from django.forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class JobSearchForm(Form):
	"""
	Basic job search form.
	"""

	keywords = 	CharField(max_length=255)
	days =		IntegerField(initial=3)
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


	def __json__(self):
		return self.cleaned_data


class UserForm(UserCreationForm):
	"""
	Form for registering and changing account details.
	"""

	error_css_class = 'error'
	required_css_class = 'required'

	def __init__(self, *args, **kwargs):
		"""
		Set default value for form fields that aren't directly mapped to the model.
		"""
		instance = kwargs.get('instance')
		if instance:
			initial = kwargs.get('initial') or {}
			if not initial.get('username'):
				initial['username'] = instance.username
			kwargs['initial'] = initial

		super(UserForm, self).__init__(*args, **kwargs)

	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']


	def save(self, commit=True):
		user = super(UserForm, self).save(commit=False)
		user.username = self.cleaned_data['username']
		if commit:
			user.save()
		return user
		

