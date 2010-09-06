from django.contrib import admin
from ipss.web.models import *

class MemberAdmin(admin.ModelAdmin):
    list_display = ['fullname','admitted']
    
class MemberAdmin(admin.ModelAdmin):
    list_display = ['title','pubdate','category','reporter']

admin.site.register(Member,MemberAdmin)
admin.site.register(Occupation)
admin.site.register(City)
admin.site.register(Tempreg)
admin.site.register(Subscription)
admin.site.register(Category)
admin.site.register(Blog)

