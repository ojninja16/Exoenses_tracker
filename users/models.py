from django.db import models
from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    email = models.CharField(max_length=255, unique=True)
    mobile_number = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.email


# Create your models here.
