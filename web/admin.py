from django.contrib import admin
from ipss.web.models import *

#class MeetingAdmin(admin.ModelAdmin):
    #class Media:
        #js = ('/sitemedia/js/tiny_mce/jscripts/tiny_mce/tiny_mce.js',
              #'/sitemedia/js/tiny_mce/jscripts/tiny_mce/textareas.js',)

admin.site.register(Member)
admin.site.register(Occupation)
admin.site.register(City)
admin.site.register(Tempreg)
admin.site.register(Subscription)
