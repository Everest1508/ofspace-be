from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSettings(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ar', 'العربية (Arabic)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_settings')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    email_notifications = models.BooleanField(default=False)
    include_logo_in_reports = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.user.username}"
