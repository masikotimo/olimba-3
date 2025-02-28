from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Achievement

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'points', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'created_at')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('points',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('points',)}),
    )
    search_fields = ('username', 'email')
    ordering = ('-points',)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'unlocked_at')
    list_filter = ('unlocked_at',)
    search_fields = ('title', 'description', 'user__username')