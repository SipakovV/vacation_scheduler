from django.contrib import admin

from .models import Employee, Department, Vacation

# Register your models here.


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'department', 'replaces', 'rating', 'entry_date', 'vacation_days')
    list_display_links = ('last_name', 'first_name', 'middle_name',)
    search_fields = ('last_name', 'first_name', 'middle_name', 'department')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'full_title',)
    list_display_links = ('title', 'full_title',)
    search_fields = ('title', 'full_title',)


class VacationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start', 'end', 'relevance')
    search_fields = ('employee',)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Vacation, VacationAdmin)
