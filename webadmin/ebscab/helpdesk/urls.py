import os
from helpdesk import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('helpdesk.views',
                       (r'^$', 'index'),
                       (r'^login/$', '_login'),
                      )