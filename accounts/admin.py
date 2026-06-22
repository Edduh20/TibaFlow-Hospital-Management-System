from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'employee_id', 'is_active')
    list_filter = ('role', 'is_active', 'department')
    search_fields = ('username', 'email', 'employee_id', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'employee_id', 'department')
        }),
    )

admin.site.register(User, CustomUserAdmin)