from django.conf.urls.defaults import *
import jobsite_main.views


### ADMIN			###
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', jobsite_main.views.index),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
