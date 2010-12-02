"""
 Callback actions for Oauth.
"""

from oauth_access.callback import AuthenticationCallback, Callback
from django.contrib.auth import login
from django.contrib.auth.models import User
from oauth_access.utils.anyetree import etree

from jobsite_main.util import auto_authenticate
from jobsite_main import db


def linked_in(request, access, token):
	a = LinkedIn()
	return a(request, access, token)


# TODO: move this out
class UserData(object):
	
	def __init__(self, id, first, last):
		self.id = id
		self.first = first
		self.last = last


class LinkedIn(Callback):

	# TODO: change to async callback
	REDIRECT_URL = '/'
	BASE_URL = 'https://api.linkedin.com'

	def redirect_url(self, request):
		return self.REDIRECT_URL


	def fetch_user_data(self, request, access, token):
		"""
		Perform an API call to retrieve data about the profile that
		was just authenticated.
		"""
		resp = access.make_api_call('xml', 
				self.BASE_URL + '/v1/people/~:(id,first-name,last-name,industry)', token)

		ud = UserData(resp.find('id').text, resp.find('first-name').text, resp.find('last-name').text)
		return ud		

	def identifier_from_data(self, data):
		return "linkedin-%s" % data.id 

	def handle_no_user(self, request, access, token, user_data):
		# create django user
		user = User.objects.create_user(self.identifier_from_data(user_data), '')
		user.first_name = user_data.first
		user.last_name = user_data.last
		user.save()

		session_id = request.session.session_key
		auto_authenticate(user)
		login(request, user)
		db.update_action_with_user_id(session_id, user)
		return user

	def handle_unauthenticated_user(self, request, user, access, token, user_data):
		session_id = request.session.session_key
		auto_authenticate(user)
		login(request, user)
		db.update_action_with_user_id(session_id, user)

