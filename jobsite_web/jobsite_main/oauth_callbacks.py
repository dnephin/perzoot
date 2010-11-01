"""
 Callback actions for Oauth.
"""

from oauth_access.callback import AuthenticationCallback, Callback


def linked_in(request, access, token):
	a = LinkedIn()
	return a(request, access, token)


class LinkedIn(AuthenticationCallback):

	def redirect_url(self, request):
		return '/'

