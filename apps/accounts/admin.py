from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'role', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['role', 'is_verified', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('Extended Info', {
            'fields': ('role', 'avatar', 'bio', 'phone', 'website', 'is_verified'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extended Info', {
            'fields': ('email', 'role'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'headline', 'rating', 'total_earnings', 'is_available']
    list_filter = ['is_available']
    search_fields = ['user__username', 'user__email', 'headline']
