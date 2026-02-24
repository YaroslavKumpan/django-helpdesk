from django.contrib import admin
from django.utils import timezone
from .models import SupportRequest, SupportMessage, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "user", "created_at")
    list_filter = ("status", "created_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Пользователь видит только свои заявки
        if request.user.profile.role == "user":
            return qs.filter(user=request.user.profile)
        # Поддержка и админ видят все
        else:
            return qs

    def get_fields(self, request, obj=None):
        """Какие поля показывать в форме редактирования"""
        if obj:  # Если редактируем существующую заявку
            # Определяем поля в зависимости от роли
            if request.user.profile.role == "user":
                return ["title", "description"]  # Пользователь видит только эти поля
            else:
                return ["title", "description", "status"]  # Поддержка видит статус тоже
        else:  # Если создаем новую заявку
            return ["title", "description"]  # Все создают заявки одинаково

    def get_readonly_fields(self, request, obj=None):
        """Поля только для чтения"""
        if obj:  # При редактировании
            if request.user.profile.role == "user":
                return ["status"]  # Пользователь не может менять статус
        return []

    def save_model(self, request, obj, form, change):
        """Сохранение заявки"""
        if not change:  # Если это новая заявка
            obj.user = request.user.profile  # Назначаем текущего пользователя
            obj.status = "new"  # Ставим статус "new"

        super().save_model(request, obj, form, change)


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "support_request", "created_at")
