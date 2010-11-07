"""
 Admin classes - Perzoot
"""

from django.contrib import admin
from jobsite_main.models import *

admin.site.register(UserEvent)
admin.site.register(LinkedAccount)
admin.site.register(SitePage)
admin.site.register(SearchEvent)
