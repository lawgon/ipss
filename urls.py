from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    url(r'^add/(?P<model_name>\w+)/?$', 'tekextensions.views.add_new_model'),
    url(r'^login/$','django.contrib.auth.views.login',   name='login'),
    url(r'^logout/$','django.contrib.auth.views.logout', name='logout'),
    (r'', include('web.urls')),
    #password
    url(r'^password_change/$', 'django.contrib.auth.views.password_change',name='password_change'),
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done',name='password_change_done'),
    url(r'^passwordreset/$','django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^passwordreset/done/$','django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$','django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',name='password_reset_complete'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
