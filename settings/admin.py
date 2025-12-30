from django.contrib import admin
from .models import UserSettings

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'language', 'email_notifications', 'include_logo_in_reports', 'updated_at']
    list_filter = ['language', 'email_notifications', 'include_logo_in_reports']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
