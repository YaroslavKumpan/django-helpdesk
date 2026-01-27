from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("support", "Support"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        choices=ROLE_CHOICES,
        max_length=20,
        default="user",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class SupportRequest(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("at_work", "At Work"),
        ("closed","Сlosed"),
        ("rejected","Rejected")
    )

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="support_requests"
    )

    title = models.CharField(max_length=255,)
    description = models.TextField(blank=True, null=True)

    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=20,
        default="new",
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class SupportMessage(models.Model):
    pass
