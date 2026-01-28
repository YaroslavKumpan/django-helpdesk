from django.contrib.auth.models import User
from django.db import models


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

    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.username


class SupportRequest(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("closed","Closed"),
        ("rejected","Rejected")
    )

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="support_requests"
    )

    title = models.CharField(max_length=255,)
    description = models.TextField(blank=True)

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
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="support_messages",
        null=True,
        blank=True,
        verbose_name="Отправитель сообщения"
    )

    support_request = models.ForeignKey(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Заявка"
    )

    text = models.TextField(
        verbose_name="Текст сообщения",
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Сообщение в поддержку"
        verbose_name_plural = "Сообщения в поддержку"
        ordering = ["created_at"]

    def __str__(self):
        return f"Message #{self.id} from {self.sender.username}"
