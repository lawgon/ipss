from django.conf.urls.defaults import *
##from dtc.web.models import *

urlpatterns = patterns('ipss.web.views',
    url(r'^$', 'index', name='index'),
    url(r'^adduser/(?P<code>\d+)/$', 'adduser', name='add_user'),
    url(r'^sorry/$', 'sorry', name='sorry'),
    url(r'^status/$', 'status', name='status'),
    url(r'^home/$', 'index', name='index'),
    url(r'^news/$', 'news', name='news'),
    url(r'^newsfull/(?P<id>\d+)/$', 'newsfull', name='newsfull'),
    url(r'^addcity/$', 'addcity', name='addcity'),
    url(r'^addoccupation/$', 'addoccupation', name='addoccupation'),
    url(r'^pendingmembers/$', 'pendingmembers', name='pendingmembers'),
    url(r'^edituser/$', 'edituser', name='edituser'),
    url(r'^register/$', 'register', name='register'),
    url(r'^members/$', 'members', name='members'),
    url(r'^regthank/(?P<id>\d+)/$', 'regthank', name='reg_thank'),
    url(r'^vote/(?P<id>\d+)/$', 'vote', name='vote'),
    url(r'^addsubscription/(?P<id>\d+)/$', 'addsubscription', name='addsubscription'),
    url(r'^addevent/$', 'addevent', name='addevent'),
    url(r'^eventlist/$', 'eventlist', name='eventlist'),
    url(r'^orglist/$', 'orglist', name='orglist'),
    url(r'^addorganization/$', 'addorganization', name='addorganization'),    
    url(r'^addevent/(?P<id>\d+)/$', 'addevent', name='addevent'),
    url(r'^addorganization/(?P<id>\d+)/$', 'addorganization', name='addorganization'),
    url(r'^viewevent/(?P<id>\d+)/$', 'viewevent', name='viewevent'),
    url(r'^vieworganization/(?P<id>\d+)/$', 'vieworganization', name='vieworganization'),
    )
