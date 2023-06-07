from django.contrib import admin
from django.utils.html import format_html
from qbwc.models import ServiceAccount, Ticket, Task


class ServiceAccountAdmin(admin.ModelAdmin):
    list_display = ("app_name", "app_url", "created_on")
    list_display_links = ("app_name",)
    ordering = ["-last_update"]


class TaskAdmin(admin.ModelAdmin):
    list_display = ("ticket", "custom_method", "status", "model", "created_on", "last_update")
    # get_model_instance
    list_display_links = ("ticket",)
    list_filter = ("status", "model", "created_on")
    search_fields = ("ticket", )
    ordering = ["-last_update"]
    
    def custom_method(self, obj):
        return obj.get_model_instance()  
    custom_method.short_description = 'Custom Value'

    fields = ('ticket', 'status', "custom_field")

    def custom_field(self, obj):
        # Logic to compute the value of the custom field
        return obj.get_model_instance()  

    custom_field.short_description = 'Custom Field'


   
    # def bar_link(self):
    #     """Link to related entites in admin"""
    #     from django.shortcuts import resolve_url
    #     from django.contrib.admin.templatetags.admin_urls import admin_urlname
    #     url = resolve_url(admin_urlname(self.get_model()()._meta, 'change'), self.model_instance)
    #     return format_html('<a href="{}">{}</a>', url, str(self.model))


class TaskInlines(admin.TabularInline):
    model = Task
    fileds = ("status", "method", )
    readonly_fileds = (
        "status",
        "method",
    )
    extra = 0
    # list_display_links = ('ticket',)
    # ordering = ['-last_update']


class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket", "status", "batch_id", "created_on", "last_update")
    list_display_links = ("ticket",)
    ordering = ["-last_update"]
    search_fields = ("ticket", "created_on", )

    list_filter = ("status", "created_on", )

    inlines = (TaskInlines,)


# admin.site.register(ServiceAccount, ServiceAccountAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(ServiceAccount, ServiceAccountAdmin)
