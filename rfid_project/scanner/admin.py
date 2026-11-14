from django.contrib import admin
from .models import User, RFIDCard, ReliefLog

class NoDeleteAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(User, NoDeleteAdmin)
admin.site.register(ReliefLog, NoDeleteAdmin)
admin.site.register(RFIDCard, NoDeleteAdmin)

