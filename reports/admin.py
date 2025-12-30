from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['service_details', 'account_number', 'service_location', 'created_by', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'foundation_year']
    search_fields = ['service_details', 'account_number', 'service_location', 'created_by__username', 'created_by__email']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Service Information', {
            'fields': ('service_details', 'account_number', 'service_location', 'foundation_year')
        }),
        ('Usage & User Information', {
            'fields': ('usage_details', 'user_biometric', 'credit_limit')
        }),
        ('Bill Reports', {
            'fields': ('monthly_bill_report', 'annual_bill_report')
        }),
        ('Comments & Notifications', {
            'fields': ('notifications_comments',)
        }),
        ('Service Recipient', {
            'fields': ('service_recipient_at_branch',)
        }),
        ('Service Reports', {
            'fields': ('monthly_service_reports', 'annual_service_reports')
        }),
        ('Metadata', {
            'fields': ('created_by', 'is_active', 'created_at', 'updated_at')
        }),
    )
