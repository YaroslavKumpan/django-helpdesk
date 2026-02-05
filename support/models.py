from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("support", "Support"),
        ("admin", "Admin"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    role = models.CharField(
        choices=ROLE_CHOICES,
        max_length=20,
        default="user",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_support(self):
        return self.role in ["support", "admin"]


class SupportRequest(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("closed", "Closed"),
    )

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="support_requests",
        verbose_name="Пользователь",
    )

    title = models.CharField(max_length=255, verbose_name="Заголовок")

    description = models.TextField(blank=True, verbose_name="Описание")

    status = models.CharField(
        choices=STATUS_CHOICES, max_length=20, default="new", verbose_name="Статус"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    updated_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Заявка в поддержку"
        verbose_name_plural = "Заявки в поддержку"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # При обновлении заявки обновляем дату
        if self.pk:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class SupportMessage(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="support_messages",
        verbose_name="Отправитель",
    )

    support_request = models.ForeignKey(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Заявка",
    )

    text = models.TextField(verbose_name="Текст сообщения")

    read = models.BooleanField(default=False, verbose_name="Прочитано")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    class Meta:
        verbose_name = "Сообщение в поддержку"
        verbose_name_plural = "Сообщения в поддержку"
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"Сообщение от {self.sender.username} (заявка #{self.support_request.id})"
        )
