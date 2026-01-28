from django.contrib import admin
from .models import SupportRequest, SupportMessage, UserProfile

class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at', 'user']  # Показать столбцы
    search_fields = ['title', 'status']  # Добавить поиск

class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ['support_request', 'sender', 'created_at']  # Показать столбцы
    search_fields = ['text']  # Добавить поиск по тексту

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']  # Показать столбцы


admin.site.register(SupportRequest, SupportRequestAdmin)
admin.site.register(SupportMessage, SupportMessageAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
