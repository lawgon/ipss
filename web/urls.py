from django.conf.urls.defaults import *
##from dtc.web.models import *

urlpatterns = patterns('ipss.web.views',
    url(r'^$', 'index', name='index'),
    #url(r'^home/$', 'home', name='home'),
    #meeting
    url(r'^addcity/$', 'addcity', name='addcity'),
    url(r'^edituser/$', 'edituser', name='edituser'),
    url(r'^edituser/$', 'edituser', name='edit_user'),
    url(r'^register/$', 'register', name='register'),
    url(r'^regthank/(?P<id>\d+)/$', 'regthank', name='reg_thank'),
    )
