from django.contrib import admin
from django.contrib.auth.models import User

from clients.models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'full_address')
    list_display_links = ('user', 'company_name')
    search_fields = ('user__username', 'company_name')
    list_filter = ('user__is_active',)
    ordering = ('user__username',)
    class Meta:
        model = Client


