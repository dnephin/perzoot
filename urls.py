from django.conf.urls.defaults import *
import jobsite_main.views
from django.conf import settings


### ADMIN			###
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', jobsite_main.views.index),
	(r'^search$', jobsite_main.views.search),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	(r'^m/(?P<path>.*)$', 'django.views.static.serve',
	        {'document_root': settings.MEDIA_ROOT}),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
