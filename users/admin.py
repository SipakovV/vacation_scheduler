from django.contrib import admin

from .models import User#, Department

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'bound_employee', 'department_manager')
    list_display_links = ('username', 'bound_employee')
    search_fields = ('username', 'bound_employee')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    search_fields = ('title',)


admin.site.register(User, UserAdmin)
#admin.site.register(Department, DepartmentAdmin)
