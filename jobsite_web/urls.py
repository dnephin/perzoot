"""
 Perzoot
 Root url configuration
"""

from django.conf.urls.defaults import *
import jobsite_main.views
from django.conf import settings
from django.views.generic.simple import direct_to_template

import oauth_access.urls


### ADMIN
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	# Pages
	(r'^$', 'jobsite_main.views.index'),
	(r'^main$', 'jobsite_main.views.main'),
	(r'^search$', 'jobsite_main.views.search'),

	# Static pages
	url(r'^page/(?P<page_name>\w+)', jobsite_main.views.static_page,
		name='static_page'),

	# Ajax only
	url(r'^jax/track/(?P<event_name>\w+)/(?P<posting_id>\d+)/$', 
			jobsite_main.views.track_event, name='track'),
	url(r'^jax/search/history$', jobsite_main.views.search_history, 
			name='search_history'),
	url(r'^jax/search/saved$', jobsite_main.views.search_history, 
			{'saved': True}, name='saved_searches'),
	url(r'^jar/search/save$', jobsite_main.views.save_search),
	url(r'^jax/postings/favs$', jobsite_main.views.favorite_postings),

	# Dev only
	(r'^m/(?P<path>.*)$', 'django.views.static.serve', 
			{'document_root': settings.MEDIA_ROOT}),

	# User/Auth
	(r'^logout$', jobsite_main.views.logout, {}, 'logout'),
	(r'^login$', jobsite_main.views.login, {}, 'login'),
	(r'^register$', jobsite_main.views.register, {}, 'register'),
	(r'^user/update_field$', jobsite_main.views.user_field_update, {}, 
			'user_field_update'),
	(r'^user$', jobsite_main.views.user_view, {}, 'user_view'),
	(r'^auth_status$', jobsite_main.views.handle_auth_block, {}, 'auth_status'),
	(r'^auth/(?P<service>\w+)$', jobsite_main.views.auth_frame_wrapper, 
			{}, 'auth_wrapper'),

	# Misc
	(r'^js_statics.js$', direct_to_template, {'template': 'js_statics.js',
			'mimetype': 'text/javascript'}),

	# OAuth
    (r'^oauth/', include(oauth_access.urls)),

	# Admin
    (r'^admin/', include(admin.site.urls)),
)
