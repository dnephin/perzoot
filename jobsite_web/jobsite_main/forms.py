"""
	Forms
"""

from django.forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core import validators


class SearchFilterWidget(HiddenInput):
	"""
	HiddenInput widget that properly turns value into a pipe delimited list.
	"""

	def _format_value(self, value):
		return "|".join(value) if value else ""


class SearchFilterField(Field):
	"""
	This field expects a list of values for the filter pipe seperated.
	Default widget is HiddenInput
	"""
	default_error_messages = {
		'required': u'This field is required.',
		'invalid': u'Search Filter is not valid.',
	}

	def __init__(self, required=False, label=None, initial=None, 
			widget=SearchFilterWidget, help_text=None, max_length=200):

		super(SearchFilterField, self).__init__(required=required, label=label,
				initial=initial, widget=widget, help_text=help_text)

		if max_length is not None:
			self.validators.append(validators.MaxLengthValidator(max_length))
		self.validators.append(validators.RegexValidator(
				regex="[\w ,\-\.]+", message="Invalid character in search filter."))


	def clean(self, value):
		"""
		Validates that each item in the filter list is clean, and returns the
		lost.

		Raises ValidatationError on errors.
		"""
		if not value:
			return ""

		# this is necessary because when deserialized from a SearchEvent this 
		# value is already a list
		if not isinstance(value, list):
			value = value.split("|")

		self.validate(value)
		for sub_value in value:
			self.run_validators(sub_value)
		return value




class JobSearchForm(Form):
	"""
	Basic job search form.
	"""

	SORT_CHOICES = (
		('date', 'date'),
		('relevancy', 'relevancy'),
	)

	search_event =	IntegerField(widget=HiddenInput, required=False)
	keywords = 	CharField(max_length=255)
	days =		IntegerField(initial=3)
	city = 		CharField(max_length=200, initial='Montreal')
	start =		IntegerField(widget=HiddenInput, initial=0, required=False)
	rows = 		IntegerField(widget=HiddenInput, initial=20, required=False)
	sort = 		ChoiceField(choices=SORT_CHOICES, required=False)
	filter_date = 		SearchFilterField()
	filter_category =	SearchFilterField()
	filter_domain = 	SearchFilterField()
	filter_company = 	SearchFilterField()


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
		data = {}
		if hasattr(self, 'cleaned_data'):
			data.update(self.cleaned_data)

		if hasattr(self, 'errors'):
			data['errors'] = self.errors
		return data


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
		

