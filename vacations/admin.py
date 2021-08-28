from django.contrib import admin

from .models import Employee, Department, Vacation

# Register your models here.


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'replaces', 'rating', 'entry_date', 'vacation_days')
    list_display_links = ('name',)
    search_fields = ('name', 'department')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    search_fields = ('name',)


class VacationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start', 'end')
    search_fields = ('employee',)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Vacation, VacationAdmin)
