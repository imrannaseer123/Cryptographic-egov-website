from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'role', 'created_at', 'is_active']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['id']
    readonly_fields = ['id', 'username_encrypted', 'password_encrypted', 'created_at']

    def has_add_permission(self, request):
        return False  # Prevent creating users through admin for security

    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing encrypted data through admin