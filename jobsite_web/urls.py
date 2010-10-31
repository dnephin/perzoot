"""
 Perzoot
 Root url configuration
"""

from django.conf.urls.defaults import *
import jobsite_main.views
from django.conf import settings


### ADMIN
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	# Pages
	(r'^$', jobsite_main.views.index),
	(r'^search$', jobsite_main.views.search),

	# Static pages
	url(r'^page/(?P<page_name>\w+)', jobsite_main.views.static_page,
		name='static_page'),

	# Ajax only
	url(r'^track/(?P<event_name>\w+)/(?P<posting_id>\d+)/$', 
		jobsite_main.views.track_event, name='track'),

	# Dev only
	(r'^m/(?P<path>.*)$', 'django.views.static.serve',
	        {'document_root': settings.MEDIA_ROOT}),

	# Admin
    (r'^admin/', include(admin.site.urls)),
)
