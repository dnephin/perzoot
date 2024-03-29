"""
	Forms
"""

import itertools
from django.forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core import validators

from jobsite_main.models import SearchEvent, SearchFilter, ContactUs


class SearchFilterWidget(HiddenInput):
	"""
	HiddenInput widget that properly turns value into a pipe delimited list.
	"""

	def _format_value(self, value):
		if not value:
			return ""
		if isinstance(value, list):
			return "|".join(value)
		return value


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




class JobSearchForm(ModelForm):
	"""
	Basic job search form.
	"""

	class Meta:
		model = SearchEvent
		fields = ('keywords', 'days', 'city', 'sort')

	search_event =		IntegerField(widget=HiddenInput, required=False)
	days =		IntegerField(initial=3)
	city = 		CharField(max_length=200, initial='Montreal')
	start =		IntegerField(widget=HiddenInput, initial=0, required=False)
	rows = 		IntegerField(widget=HiddenInput, initial=20, required=False)
	sort = 		ChoiceField(choices=SearchEvent.SORT_CHOICES, required=False)
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

		# Update filters values to pipe separated list
		for filter in itertools.ifilter(
				lambda f: f.startswith('filter_'), data.keys()):
			data[filter] = self.fields[filter].widget._format_value(data[filter])

		if hasattr(self, 'errors'):
			data['errors'] = self.errors
		return data


	def save(self, commit=False):
		"""
		Setup the SearchEvent object to save it.
		"""
		event = super(JobSearchForm, self).save(commit=False)
		event.id = self.cleaned_data.get('search_event', None)
		return event

	def save_filters(self, event):
		"""
		Save the search filters for this search.  This must be called after 
		the search event has already been saved.
		"""
		for filter in SearchFilter.FILTER_CHOICES:
			for filter_value in self.cleaned_data.get('filter_' + filter[0], []):
				event.searchfilter_set.create(
					filter_type =  filter[0], filter_value = filter_value
				)

	@staticmethod
	def from_instance(model):
		"""
		Return a JobSearchForm instance from a model instance.
		"""
		data = {
			'search_event': model.id,
			'days': model.days,
			'city': model.city,
			'sort': model.sort,
			'keywords': model.keywords,
			}

		for filter in model.searchfilter_set.all():
			filter_name = 'filter_' + filter.filter_type

			if filter_name not in data:
				data[filter_name] = []

			data[filter_name].append(filter.filter_value)
		return JobSearchForm(data)


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
		


class ContactUsForm(ModelForm):
	"""
	Contact Us Form.
	"""

	class Meta:
		model = ContactUs

	error_css_class = 'error'
	required_css_class = 'required'
	async = BooleanField(widget=HiddenInput(), initial=False)
	
