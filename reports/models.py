from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Report(models.Model):
    # Basic Information
    service_details = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=100, blank=True)
    service_location = models.CharField(max_length=255, blank=True)
    foundation_year = models.IntegerField(null=True, blank=True)
    
    # Usage and User Information
    usage_details = models.CharField(max_length=255, blank=True)
    user_biometric = models.CharField(max_length=255, blank=True)
    credit_limit = models.CharField(max_length=100, blank=True)
    
    # Bill Reports
    monthly_bill_report = models.CharField(max_length=255, blank=True)
    annual_bill_report = models.CharField(max_length=255, blank=True)
    
    # Comments and Notifications
    notifications_comments = models.TextField(blank=True)
    
    # Service Recipient
    service_recipient_at_branch = models.CharField(max_length=255, blank=True)
    
    # Service Reports
    monthly_service_reports = models.TextField(blank=True)
    annual_service_reports = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['created_by']),
            models.Index(fields=['account_number']),
        ]
    
    def __str__(self):
        return f"{self.service_details} - {self.account_number}" if self.service_details else f"Report #{self.id}"
