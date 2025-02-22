from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings

from apis.core.models import BaseModel


def profile_image_path(instance, filename):
    return "user/profile/avatar/{}/{}".format(instance.username, filename)


class User(AbstractUser):
    ADMIN = 'admin'
    STUDENT = 'student'
    INSTRUCTOR = 'instructor'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (STUDENT, 'Student'),
        (INSTRUCTOR, 'Instructor'),
    ]

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=STUDENT)
    is_locked = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to=profile_image_path, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)


class Profile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to=profile_image_path, blank=True, null=True)  # Optional for user photo

    def __str__(self):
        return f"{self.user.username}'s profile"


class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # PIN is valid for 10 minutes and if it has not been used
        return timezone.now() < self.created_at + timedelta(minutes=10) and not self.is_used

    def __str__(self):
        return f"{self.user.email} - {self.pin}"
