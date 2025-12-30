from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.username or self.email
