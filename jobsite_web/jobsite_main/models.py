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
	user_id = ForeignKey(User, null=True)
	posting_id = IntegerField()
	event =   CharField(max_length=6, choices=EVENTS)
	tstamp =  DateTimeField(auto_now_add=True)



class LinkedAccount(Model):
	"""
	Record of an open ID account linked to their user account.
	"""
	# TODO: more details here
	user = ForeignKey(User)
	linked_account_name = CharField(max_length=25)



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


class SearchEvent(Model):
	"""
	A search that was performed for a user.
	"""

	session = CharField(max_length=40, db_index=True)
	user_id = ForeignKey(User, null=True)
	tstamp =  DateTimeField(auto_now_add=True)
	terms =   CharField(max_length=250)
	full_string = CharField(max_length=1000)


	def __str__(self):
		return "Search [%s|%s] %s" % (self.user_id, self.tstamp, self.terms)
