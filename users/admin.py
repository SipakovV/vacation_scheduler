from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser#, Department


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('username', 'bound_employee', 'is_staff', 'employees_permission_level', 'is_department_manager', 'is_active',)
    list_filter = ('username', 'bound_employee', 'is_staff', 'is_active',)
    list_display_links = ('username', 'bound_employee',)
    fieldsets = (
        (None, {'fields': ('username', 'password', 'bound_employee')}),
        ('Permissions', {'fields': ('is_department_manager', 'employees_permission_level', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'bound_employee', 'employees_permission_level',
                       'is_department_manager', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('username', 'bound_employee')
    ordering = ('-is_staff', '-employees_permission_level', '-is_department_manager', '-is_active', 'username',)


# @admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    search_fields = ('title',)



