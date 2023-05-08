from django.contrib import admin
from qbwc.models import ServiceAccount, Ticket


class ServiceAccountAdmin(admin.ModelAdmin):
    list_display = ("app_name", "app_url", "created_on")
    list_display_links = ("app_name",)
    ordering = ["-last_update"]


# class ServiceAccountAdmin(admin.ModelAdmin):
#     list_display = ('app_name', 'app_url', 'created_on')
#     list_display_links = ('app_name',)
#     ordering = ['-last_update']

# admin.site.register(ServiceAccount, ServiceAccountAdmin)
admin.site.register(Ticket)
admin.site.register(ServiceAccount, ServiceAccountAdmin)
