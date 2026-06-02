from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('STAFF', 'Staff/Volunteer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STAFF')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser

    def is_staff_volunteer(self):
        return self.role == 'STAFF'
