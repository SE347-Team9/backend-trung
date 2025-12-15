from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin cho Custom User Model
    """
    list_display = ['username', 'email', 'role', 'phone', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-created_at']
    
    # Thêm các field mới vào form
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin thêm', {
            'fields': ('role', 'phone', 'address')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin thêm', {
            'fields': ('role', 'phone', 'address')
        }),
    )
