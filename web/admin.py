from django.contrib import admin
from ipss.web.models import *

class MemberAdmin(admin.ModelAdmin):
    list_display = ['member_user_name','admitted']

admin.site.register(Member,MemberAdmin)
admin.site.register(Occupation)
admin.site.register(City)
admin.site.register(Tempreg)
admin.site.register(Subscription)
