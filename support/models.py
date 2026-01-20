from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("support", "Support"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(
        choices=ROLE_CHOICES,
        max_length=20,
        default="user",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class SupportRequest(models.Model):
    pass



class SupportMessage(models.Model):
    pass
