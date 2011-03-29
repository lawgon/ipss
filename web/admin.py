from django.contrib import admin
from ipss.web.models import *

class MemberAdmin(admin.ModelAdmin):
    list_display = ['fullname','admitted','paid']
    


admin.site.register(Member,MemberAdmin)
admin.site.register(Occupation)
admin.site.register(City)
admin.site.register(Tempreg)
admin.site.register(Subscription)
admin.site.register(Category)
admin.site.register(Blog)
admin.site.register(Vote)
admin.site.register(Organization)
