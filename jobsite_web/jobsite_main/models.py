"""
 Perzoot

 Database models.
"""

from django.db.models import *
from django.contrib.auth.models import User


class UserEvent(Model):
	"""
	Tracking for events that users can perform relating to a job posting.
	"""

	EVENTS = (
		('save','Save to list'),
		('remove', 'Remove from list'),
		('open', 'Open the posting link'),
	)

	session = CharField(max_length=40, db_index=True)
	user = ForeignKey(User, null=True)
	posting_id = CharField(max_length=32)
	event =   CharField(max_length=6, choices=EVENTS)
	tstamp =  DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('event', 'posting_id', 'session')

	def __str__(self):
		return "UserEvent [%s|%s] %s %s" % (self.user or self.session, 
				self.tstamp.strftime("%Y-%m-%d %H:%M"), self.event, 
				self.posting_id)


class SearchEvent(Model):
	"""
	A search that was performed for a user.
	"""

	SORT_CHOICES = (
		('date', 'date'),
		('relevancy', 'relevancy'),
	)

	session = 	CharField(max_length=40, db_index=True)
	user =		ForeignKey(User, null=True)
	tstamp =	DateTimeField(auto_now_add=True)
	saved =		BooleanField(default=False)
	search_type =	CharField(max_length=50)

	keywords =	CharField(max_length=255)
	days = 		IntegerField()
	city =		CharField(max_length=200)
	sort = 		CharField(choices=SORT_CHOICES, max_length=20, null=True)


	def __str__(self):
		return "Search [%s|%s] %s" % (self.user or self.session, 
				self.tstamp.strftime("%Y-%m-%d %H:%M"), self.keywords)

	# TODO: add filters and extra params
	def __json__(self):
		return {
			'id': self.id,
			'date': self.tstamp.strftime("%b %d"),
			'keywords': self.keywords,
			'saved': self.saved,
		}


class SearchFilter(Model):
	"""
	A Filter that was used on a search event.
	"""

	FILTER_CHOICES = (
		('date', 'date'),
		('category', 'category'),
		('domain', 'domain'),
		('company', 'company')
	)

	search_event =	ForeignKey(SearchEvent)
	filter_type =	CharField(choices=FILTER_CHOICES, max_length=20)
	filter_value = 	CharField(max_length=250)


	def __str__(self):
		return "SearchFilter[%s] %s = %s" % (self.search_id, 
				self.filter_type, self.filter_value)


class SitePage(Model):
	"""
	The text of a 'static' page stored by version and date.  This enables
	easier updates of pages like Terms, and About us.
	"""

	page = CharField(max_length=25, db_index=True)
	version = FloatField()
	added_date = DateTimeField(auto_now_add=True)
	updated_date = DateTimeField(auto_now_add=True, auto_now=True)
	content = TextField()
	title = CharField(max_length=200)
	active = BooleanField(default=False)

	class Meta:
		unique_together = ('page', 'version')

	def __str__(self):
		active = "DISABLED" if not self.active else ""
		return "%s page %s (version: %s, last updated: %s)" % (
				self.page, active, self.version, self.updated_date)


	def __json__(self):
		return {
			'name': self.page, 'title': self.title,
			'last_modified': self.updated_date,
			'content': self.content }


