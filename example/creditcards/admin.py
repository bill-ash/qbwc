from django.contrib import admin
from .models import CreditCard, CreditCardCharge


class CreditCardAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_on",
        "last_update",
    )
    list_display_links = ("name",)
    ordering = ("name",)


class CreditChargeAdmin(admin.ModelAdmin):
    list_display = (
        "vendor",
        "credit_card",
        "created_on",
        "last_update",
    )
    list_display_links = ("vendor",)
    ordering = ("-last_update",)
    

admin.site.register(CreditCard, CreditCardAdmin)
admin.site.register(CreditCardCharge, CreditChargeAdmin)
