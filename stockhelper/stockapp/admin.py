from django.contrib import admin

from .models import Card, Stock, User


class CustomUserAdmin(admin.ModelAdmin):
    # Show the balance in the admin table in addition to the other default fields
    list_display = ["username", "email",
                    "first_name", "last_name", "balance", "is_staff"]


admin.site.register(User, CustomUserAdmin)
admin.site.register(Card)
admin.site.register(Stock)
