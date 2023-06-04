from django.contrib import admin
from .models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "company_name", "first_name", "last_name", "created_on", "last_update",)
    list_display_links = ("name",)
    ordering = ("name", )
    
    
admin.site.register(Customer, CustomerAdmin)