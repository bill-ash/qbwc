from django.contrib import admin
from django.utils.html import format_html
from qbwc.models import ServiceAccount, Ticket, Task


class ServiceAccountAdmin(admin.ModelAdmin):
    list_display = ("app_name", "app_url", "created_on")
    list_display_links = ("app_name",)
    ordering = ["-last_update"]


class TaskAdmin(admin.ModelAdmin):
    list_display = ("ticket", "status", "model", "created_on", "last_update")
    # get_model_instance
    list_display_links = ("ticket",)

    ordering = ["-last_update"]

    # def bar_link(self):
    #     """Link to related entites in admin"""
    #     from django.shortcuts import resolve_url
    #     from django.contrib.admin.templatetags.admin_urls import admin_urlname
    #     url = resolve_url(admin_urlname(self.get_model()()._meta, 'change'), self.model_instance)
    #     return format_html('<a href="{}">{}</a>', url, str(self.model))


class TaskInlines(admin.TabularInline):
    model = Task
    fileds = ("status", "method")
    readonly_fileds = (
        "status",
        "method",
    )
    # list_display_links = ('ticket',)
    # ordering = ['-last_update']


class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket", "status", "batch_id", "created_on", "last_update")
    list_display_links = ("ticket",)
    ordering = ["-last_update"]

    inlines = (TaskInlines,)


# admin.site.register(ServiceAccount, ServiceAccountAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(ServiceAccount, ServiceAccountAdmin)
