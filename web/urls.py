from django.conf.urls.defaults import *
##from dtc.web.models import *

urlpatterns = patterns('ipss.web.views',
    url(r'^$', 'index', name='index'),
    #url(r'^home/$', 'home', name='home'),
    #meeting
    url(r'^addcity/$', 'addcity', name='addcity'),
    url(r'^edituser/$', 'edituser', name='edituser'),
    )
